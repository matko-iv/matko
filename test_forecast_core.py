"""Deterministic regression tests for forecast math and train/live parity."""

import os
import unittest

os.environ['FC_DEVICE'] = 'cpu'

import numpy as np
import pandas as pd

import forecast_48h_v3 as fc
import prob_forecast as pf


class _FakeDMatrix:
    def __init__(self, labels, weights=None):
        self._labels = np.asarray(labels, dtype=float)
        self._weights = (np.asarray(weights, dtype=float) if weights is not None
                         else np.array([], dtype=float))

    def get_label(self):
        return self._labels

    def get_weight(self):
        return self._weights


class _ConstantModel:
    def __init__(self, value):
        self.value = float(value)

    def predict(self, X):
        return np.full(len(X), self.value)


class ForecastCoreTests(unittest.TestCase):
    def test_focal_derivatives_and_sample_weights(self):
        gamma, alpha = 2.0, 0.25
        margins = np.array([-1.0, 0.0, 1.0, -1.0, 0.0, 1.0])
        labels = np.array([0, 0, 0, 1, 1, 1], dtype=float)
        objective = fc.focal_loss_xgb_objective(gamma, alpha)
        grad, hess = objective(margins, _FakeDMatrix(labels))

        def loss(z):
            p = 1.0 / (1.0 + np.exp(-z))
            pt = np.where(labels == 1, p, 1 - p)
            at = np.where(labels == 1, alpha, 1 - alpha)
            return -at * np.power(1 - pt, gamma) * np.log(pt)

        eps = 1e-4
        grad_fd = (loss(margins + eps) - loss(margins - eps)) / (2 * eps)
        hess_fd = (loss(margins + eps) - 2 * loss(margins)
                   + loss(margins - eps)) / (eps ** 2)
        np.testing.assert_allclose(grad, grad_fd, rtol=2e-5, atol=2e-6)
        np.testing.assert_allclose(hess, hess_fd, rtol=2e-4, atol=2e-5)

        weights = np.array([0.7, 1.5, 1.0, 1.4, 0.8, 2.0])
        grad_w, hess_w = objective(margins, _FakeDMatrix(labels, weights))
        np.testing.assert_allclose(grad_w, grad * weights)
        np.testing.assert_allclose(hess_w, hess * weights)

        # A very hard positive has negative exact curvature; XGBoost must see
        # the documented positive floor, not abs(negative curvature).
        _, hard_hess = objective(np.array([-5.0]), _FakeDMatrix([1.0]))
        np.testing.assert_allclose(hard_hess, [1e-3])

        metric = fc.focal_loss_xgb_feval(gamma, alpha)
        _, weighted_value = metric(margins, _FakeDMatrix(labels, weights))
        self.assertAlmostEqual(weighted_value, float(np.average(loss(margins), weights=weights)))

    def test_meteorological_metric_boundaries(self):
        perfect = fc.meteorological_metrics([0, 1, 0, 1], [0, 1, 0, 1])
        self.assertGreater(perfect['sedi'], 0.999)
        self.assertEqual(perfect['precision'], 1.0)

        always_dry = fc.meteorological_metrics([0, 1, 0, 1], [0, 0, 0, 0])
        self.assertEqual(always_dry['precision'], 0.0)
        self.assertEqual(always_dry['far'], 0.0)

    def test_pit_uses_interior_midranks(self):
        members = np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]])
        pit = fc.pit_values(np.array([0.0, 4.0]), members)
        self.assertGreater(pit[0], 0.0)
        self.assertLess(pit[1], 1.0)
        self.assertAlmostEqual(pit[0] + pit[1], 1.0)

    def test_observation_only_features_are_excluded(self):
        frame = pd.DataFrame({
            'safe_model_feature': [1.0, 2.0],
            'dry_spell_length': [5.0, 6.0],
            'monthly_clim_rain_freq': [0.1, 0.2],
            '_derived_precip_obs': [0.0, 0.2],
            '_canonical_precip_rate_mm': [0.0, 0.2],
        })
        self.assertEqual(fc.get_feature_columns(frame), ['safe_model_feature'])

    def test_temporal_cv_groups_duplicate_valid_times(self):
        unique = pd.date_range('2026-01-01', periods=400, freq='h')
        duplicated = pd.Series(np.repeat(unique.values, 3))
        splits = fc._timestamp_grouped_cv_splits(duplicated)
        self.assertEqual(len(splits), 3)
        for train_idx, val_idx in splits:
            train_times = set(duplicated.iloc[train_idx])
            val_times = set(duplicated.iloc[val_idx])
            self.assertTrue(train_times.isdisjoint(val_times))
            self.assertLessEqual(
                max(train_times), min(val_times) - pd.Timedelta(hours=72)
            )

        q_times = pd.Series(np.repeat(
            pd.date_range('2025-01-01', periods=2200, freq='h').values, 3
        ))
        q_X = pd.DataFrame({'x': np.arange(len(q_times), dtype=float)})
        q_y = pd.Series(np.arange(len(q_times), dtype=float))
        folds = fc._quantile_clock_split(q_X, q_y, q_times)
        fit_times = set(folds['time_fit'])
        val_times = set(folds['time_val'])
        cal_times = set(folds['time_cal'])
        self.assertTrue(fit_times.isdisjoint(val_times | cal_times))
        self.assertTrue(val_times.isdisjoint(cal_times))
        self.assertGreaterEqual(folds['fit_val_gap'], pd.Timedelta(hours=72))
        self.assertGreaterEqual(folds['val_cal_gap'], pd.Timedelta(hours=72))

        precip_folds = fc._precip_clock_split(q_X, q_y, q_times)
        precip_sets = [set(precip_folds[f'time_{name}'])
                       for name in ('fit', 'val', 'cal', 'gate')]
        for i, left in enumerate(precip_sets):
            for right in precip_sets[i + 1:]:
                self.assertTrue(left.isdisjoint(right))
        for gap_name in ('fit_val_gap', 'val_cal_gap', 'cal_gate_gap'):
            self.assertGreaterEqual(
                precip_folds[gap_name], pd.Timedelta(hours=72)
            )

    def test_rain_consensus_excludes_missing_members_and_counts_hours(self):
        values = pd.DataFrame({
            'a': [0.2, 0.2, np.nan, 0.0],
            'b': [0.3, np.nan, np.nan, 0.2],
            'c': [0.4, np.nan, np.nan, 0.0],
        })
        wet, available, agreement, wet_hour = fc._rain_consensus_stats(values)
        np.testing.assert_array_equal(wet.values, [3, 1, 0, 1])
        np.testing.assert_array_equal(available.values, [3, 1, 0, 3])
        np.testing.assert_allclose(
            agreement.values, [1.0, 1.0, np.nan, 1 / 3], equal_nan=True
        )
        np.testing.assert_allclose(
            wet_hour.values, [1.0, 1.0, np.nan, 0.0], equal_nan=True
        )

        frame = pd.DataFrame({
            'datetime': pd.date_range('2026-01-01', periods=4, freq='h'),
            'ARPEGE_EUROPE_precipitation_model': values['a'],
            'GFS_SEAMLESS_precipitation_model': values['b'],
            'ICON_SEAMLESS_precipitation_model': values['c'],
        })
        engineered = fc.engineer_features(frame)
        # Three wet model votes in hour 1 are one wet hour, not three.
        self.assertEqual(engineered['rain_hours_6h'].iloc[0], 1.0)
        self.assertEqual(engineered['rain_hours_6h'].iloc[1], 2.0)
        self.assertTrue(np.isnan(engineered['rain_agreement'].iloc[2]))

    def test_precip_label_qa_rejects_wet_only_missing_dry_data(self):
        n = 20
        frame = pd.DataFrame({
            'datetime': pd.date_range('2025-01-01', periods=n, freq='h'),
            'temperature_2m_obs': np.full(n, 15.0),
            'relative_humidity_2m_obs': np.full(n, 70.0),
            'pressure_msl_obs': np.full(n, 1013.0),
        })
        good = pd.Series([0.0] * 18 + [0.2, 1.0])
        report = fc._validate_precip_observations(
            frame, good, 'unit-good', min_year_rows=10
        )
        self.assertEqual(report[0]['completeness'], 1.0)
        bad = pd.Series([np.nan] * 18 + [0.2, 1.0])
        with self.assertRaisesRegex(RuntimeError, 'wet-only'):
            fc._validate_precip_observations(
                frame, bad, 'unit-bad', min_year_rows=10
            )

    def test_onset_age_and_cdf_do_not_split_equal_age(self):
        frame = pd.DataFrame({
            '_derived_precip_obs': [0.0, 0.0, 0.0, 0.2, 0.2, 0.0],
            'datetime': pd.date_range('2026-01-01', periods=6, freq='h'),
            'feature': np.arange(6, dtype=float),
        })
        X, y, _ = fc.build_onset_person_period(frame, ['feature'])
        np.testing.assert_array_equal(X['dry_age'].values, [1, 2, 3, 3, 1])
        np.testing.assert_array_equal(y.values, [0, 0, 0, 1, 0])

        live_age = fc._forecast_onset_dry_age([0.0, 0.0, 0.0, 0.2])
        np.testing.assert_array_equal(live_age, [1, 2, 3, 3])
        cdf = fc._onset_cdf_from_hazard([0.1, 0.1, 0.1, 0.1], [1, 2, 3, 3])
        self.assertTrue(np.all(np.diff(cdf) > 0))
        self.assertAlmostEqual(cdf[-1], 1 - 0.9 ** 4)

        live_age_unknown = fc._forecast_onset_dry_age([0.0, np.nan, 0.0])
        np.testing.assert_allclose(live_age_unknown, [1.0, np.nan, 1.0], equal_nan=True)
        cdf_unknown = fc._onset_cdf_from_hazard(
            [0.1, 0.1, 0.1, 0.1], [1.0, np.nan, 1.0, 2.0]
        )
        np.testing.assert_allclose(cdf_unknown, [0.1, np.nan, 0.1, 0.19], equal_nan=True)

        # Capped age must not collapse a genuine two-hour timing miss to zero.
        pred_hours, obs_hours = fc._onset_event_hours(
            [0.01, 0.2, 0.01, 0.01], [0, 0, 0, 1], [47, 48, 48, 48],
            pd.date_range('2026-01-02', periods=4, freq='h'), threshold=0.1,
        )
        self.assertEqual(pred_hours, [1.0])
        self.assertEqual(obs_hours, [3.0])
        self.assertEqual(fc.onset_timing_metrics(pred_hours, obs_hours)['mae_hours'], 2.0)

        raw_features = pd.DataFrame({
            'datetime': pd.date_range('2026-01-01', periods=3, freq='h'),
            'humidity': [60.0, 70.0, 80.0],
            'agreement': [0.0, 0.5, 1.0],
            # Live previous-run features can arrive as integer columns.  The
            # shift adds a trailing NaN, which must widen rather than fail.
            'previous_run_humidity': [51, 48, 45],
        })
        aligned = fc._align_onset_features_to_display(raw_features)
        pd.testing.assert_series_equal(
            aligned['datetime'], raw_features['datetime'], check_names=False
        )
        np.testing.assert_allclose(
            aligned['humidity'], [70.0, 80.0, np.nan], equal_nan=True
        )
        np.testing.assert_allclose(
            aligned['agreement'], [0.5, 1.0, np.nan], equal_nan=True
        )
        np.testing.assert_allclose(
            aligned['previous_run_humidity'], [48.0, 45.0, np.nan], equal_nan=True
        )

    def test_shared_stack_and_blend_dispatcher(self):
        X = pd.DataFrame({'x': [0.0, 1.0]})
        frame = pd.DataFrame({'baseline': [10.0, 20.0]})
        bundle = {
            'direct_model': _ConstantModel(1),
            'resid_model': _ConstantModel(2),
            'mse_model': _ConstantModel(3),
            'method': 'stacked',
            'stack_weights': (0.2, 0.3, 0.5),
        }
        stacked = fc._predict_nonprecip_bundle(bundle, X, frame, 'baseline')
        expected_stack = 0.2 * 1 + 0.3 * (frame['baseline'].values + 2) + 0.5 * 3
        np.testing.assert_allclose(stacked, expected_stack)

        bundle['method'] = 'blend'
        bundle['blend_alpha'] = 0.6
        blended = fc._predict_nonprecip_bundle(bundle, X, frame, 'baseline')
        np.testing.assert_allclose(
            blended, 0.6 * expected_stack + 0.4 * frame['baseline'].values
        )

        broken = dict(bundle)
        broken['resid_model'] = None
        with self.assertRaisesRegex(ValueError, 'resid_model'):
            fc._predict_nonprecip_bundle(broken, X, frame, 'baseline')

    def test_cloud_postprocessor_is_shared_and_deterministic(self):
        frame = pd.DataFrame({
            'datetime': pd.to_datetime([
                '2026-07-01 08:00', '2026-07-01 12:00', '2026-01-01 16:00'
            ]),
            'cloud_cover_ens_mean': [20.0, 5.0, 95.0],
        })
        out = fc._postprocess_cloud_prediction([90.0, 90.0, 10.0], frame)
        # Outside the seasonal windows use ensemble; inside, apply low-ensemble cap.
        np.testing.assert_allclose(out, [20.0, 35.0, 95.0])

    def test_quantile_tail_exceedance_decays(self):
        qdf = pd.DataFrame({
            'q05': [1.0], 'q10': [1.2], 'q25': [1.5], 'q50': [2.0],
            'q75': [2.5], 'q90': [3.0], 'q95': [3.5],
        })
        p_at_q95 = pf.exceedance_from_quantiles(qdf, pf.DEFAULT_ALPHAS, 3.5)[0]
        p_10 = pf.exceedance_from_quantiles(qdf, pf.DEFAULT_ALPHAS, 10.0)[0]
        p_17 = pf.exceedance_from_quantiles(qdf, pf.DEFAULT_ALPHAS, 17.0)[0]
        self.assertAlmostEqual(p_at_q95, 0.05)
        self.assertGreater(p_10, p_17)
        self.assertLess(p_17, 1e-6)

        tied = qdf.copy()
        tied['q90'] = tied['q95']
        just_above = pf.exceedance_from_quantiles(
            tied, pf.DEFAULT_ALPHAS, float(tied['q95'].iloc[0]) + 1e-6
        )[0]
        farther = pf.exceedance_from_quantiles(tied, pf.DEFAULT_ALPHAS, 10.0)[0]
        self.assertAlmostEqual(just_above, 0.05, places=5)
        self.assertGreater(just_above, farther)

    def test_ecc_uses_integer_rank_indices(self):
        alphas = pf.DEFAULT_ALPHAS
        qdf = pd.DataFrame({
            f'q{int(round(a * 100)):02d}': [a * 10.0, a * 20.0]
            for a in alphas
        })
        raw = np.array([
            [1.0, 2.0, 3.0, 4.0],
            [4.0, 3.0, np.nan, 1.0],
        ])
        scenarios = pf.ecc_scenarios(qdf, alphas, raw)
        self.assertEqual(scenarios.shape, raw.shape)
        self.assertTrue(np.isfinite(scenarios).all())
        self.assertTrue(np.all(np.diff(scenarios[0]) > 0))
        self.assertGreater(scenarios[1, 0], scenarios[1, -1])

    def test_cqr_uses_conservative_order_statistic_and_crps_integral(self):
        X = pd.DataFrame({'x': np.arange(100, dtype=float)})
        models = {0.05: _ConstantModel(0.0), 0.95: _ConstantModel(0.0)}
        offsets = pf.cqr_calibrate(
            models, X, np.arange(100, dtype=float), pairs=((0.05, 0.95),)
        )
        # NumPy's conservative 'higher' selection at the finite-sample level.
        self.assertEqual(offsets[(0.05, 0.95)], 91.0)

        alphas = [0.05, 0.25, 0.50, 0.90]
        point = pd.DataFrame({
            f"q{int(round(a * 100)):02d}": [2.0, 2.0] for a in alphas
        })
        # A degenerate predictive distribution has CRPS == absolute error.
        self.assertAlmostEqual(
            pf.crps_from_quantiles([1.0, 3.0], point, alphas=alphas), 1.0
        )
        self.assertEqual(
            pf.crps_from_quantiles([2.0, 2.0], point, alphas=alphas), 0.0
        )

    def test_daily_rain_consensus_excludes_models_without_data(self):
        raw = pd.DataFrame({
            'ARPEGE_EUROPE_precipitation_model': [0.0, 0.0],
            'GFS_SEAMLESS_precipitation_model': [np.nan, np.nan],
            'ICON_SEAMLESS_precipitation_model': [np.nan, 0.2],
        })
        # One dry vote + one wet vote; the unavailable model is not a dry vote.
        self.assertEqual(fc._daily_model_rain_probability(raw), 50)
        self.assertIsNone(fc._daily_model_rain_probability(pd.DataFrame(index=[0, 1])))

    def test_dm_and_weather_direction_edge_cases(self):
        delta = np.array([-2, -1, 0, 1, 2, 2, 1, 0, -1, -2], dtype=float)
        dm, p = pf.dm_test_hln(10 + delta / 2, 10 - delta / 2, h=2)
        self.assertTrue(np.isfinite(dm) and np.isfinite(p))
        self.assertAlmostEqual(dm, 0.0)
        self.assertAlmostEqual(p, 1.0)

        alternating = np.array([0, 1] * 5, dtype=float)
        dm_degenerate, p_degenerate = pf.dm_test_hln(
            alternating, 1 - alternating, h=8
        )
        self.assertTrue(np.isnan(dm_degenerate) and np.isnan(p_degenerate))

        snow = pd.Series({
            'weather_code_raw': 71,
            'precipitation_xgb': 0.0,
            'cloud_cover_xgb': 10.0,
        })
        self.assertEqual(fc.correct_weather_code_row(snow), 71)

        directions = pd.DataFrame([[350.0, 10.0]])
        mean_dir = float(fc._circular_mean_degrees(directions).iloc[0])
        self.assertTrue(mean_dir < 1.0 or mean_dir > 359.0)
        cancelling = fc._circular_mean_degrees(pd.DataFrame([[0.0, 180.0]])).iloc[0]
        self.assertTrue(np.isnan(cancelling))


class MarineLogicTests(unittest.TestCase):
    def test_direction_capped_sea_state(self):
        # Jugo (SE) keeps the full Douglas scale.
        self.assertEqual(fc.adriatic_sea_state(2.0, 140.0), 4)
        # Bura (NE) chop never rates above "Talasasto" regardless of height.
        self.assertEqual(fc.adriatic_sea_state(3.0, 45.0), 4)
        # Waves "from" N or W come off the land: capped at "Blagi talasi",
        # so 0.8 m from those sectors can no longer show "Umjereni talasi".
        self.assertEqual(fc.adriatic_sea_state(0.8, 0.0), 2)
        self.assertEqual(fc.adriatic_sea_state(0.8, 270.0), 2)
        self.assertEqual(fc.adriatic_sea_state(0.8, 350.0), 2)
        # Unknown direction leaves the plain Douglas state; no height -> None.
        self.assertEqual(fc.adriatic_sea_state(0.8, None), 3)
        self.assertIsNone(fc.adriatic_sea_state(None, 140.0))

    def test_sailing_score_is_strict(self):
        self.assertEqual(fc.sailing_score(2, 0.2), ("green", "Idealno"))
        self.assertEqual(fc.sailing_score(3, 0.5), ("green", "Dobro"))
        # Bft 4 or a metre of wave is no longer "Dobro".
        self.assertEqual(fc.sailing_score(4, 0.8), ("yellow", "Prihvatljivo"))
        self.assertEqual(fc.sailing_score(5, 1.5), ("orange", "Oprez"))
        self.assertEqual(fc.sailing_score(6, 1.0), ("red", "Opasno"))
        self.assertEqual(fc.sailing_score(3, 2.0), ("red", "Opasno"))
        self.assertEqual(fc.sailing_score(None, 1.0), ("gray", "N/A"))

    def test_hail_votes_from_model_codes(self):
        # WMO 96/99 votes per hour, shifted -1 to the start-of-hour convention
        # (Open-Meteo labels the preceding hour, same as precipitation).
        m1, m2 = fc.MODELS[0], fc.MODELS[1]
        dts = pd.date_range('2026-07-25 12:00', periods=4, freq='h')
        raw = pd.DataFrame({
            'datetime': dts,
            f'{m1}_weather_code_model': [95, 96, 96, 95],
            f'{m2}_weather_code_model': [95, 95, 99, 0],
        })
        votes = fc._hail_votes_by_datetime(raw)
        self.assertEqual(votes, {dts[0]: 1, dts[1]: 2})
        self.assertEqual(fc._hail_votes_by_datetime(None), {})
        self.assertEqual(fc._hail_votes_by_datetime(
            pd.DataFrame({'datetime': dts})), {})

    def test_daily_wind_consensus_keeps_model_peaks(self):
        # Ensemble-mean wind flattens to ~1.5 m/s, but each model's own daily
        # max is 4 and 6: the consensus field must carry their median so
        # long-range days stop all reading "slab".
        dts = pd.date_range('2026-07-25', periods=24, freq='h')
        grp = pd.DataFrame({
            'datetime': dts,
            'hour': list(range(24)),
            'temperature_2m_ensemble': [25.0] * 24,
            'wind_speed_10m_ensemble': [1.5] * 24,
            'wind_gusts_10m_ensemble': [3.0] * 24,
            'precipitation_ensemble': [0.0] * 24,
            'relative_humidity_2m_ensemble': [60.0] * 24,
            'pressure_msl_ensemble': [1013.0] * 24,
            'cloud_cover_ensemble': [20.0] * 24,
            'weather_code': [1.0] * 24,
        })
        m1, m2 = fc.MODELS[0], fc.MODELS[1]
        fc_raw = pd.DataFrame({
            'datetime': dts,
            f'{m1}_wind_speed_10m_model': [4.0] * 24,
            f'{m2}_wind_speed_10m_model': [6.0] * 24,
            f'{m1}_precipitation_model': [0.0] * 24,
        })
        ds = fc._build_daily_summary('2026-07-25', 'Saturday', grp, fc_raw=fc_raw)
        self.assertEqual(ds['wind_max'], 1.5)
        self.assertEqual(ds['wind_max_models'], 5.0)

    def test_daily_narrative_mentions_short_rain(self):
        # A clear summer day with a single 0.15 mm shower hour (total 0.2 mm,
        # below the old 0.2 mm gate) must still carry the rain note.
        precip = [0.0] * 24
        precip[14] = 0.15
        precip[15] = 0.05
        grp = pd.DataFrame({
            'hour': list(range(24)),
            'cloud_cover': [20.0] * 24,
            'precipitation': precip,
            'wind_speed_10m': [3.0] * 24,
            'wind_gusts_10m': [5.0] * 24,
            'temperature_2m': [26.0] * 24,
            'weather_code': [1.0] * 24,
            'wind_direction_10m': [180.0] * 24,
        })
        narrative = fc._daily_narrative(grp)['narrative'].lower()
        self.assertTrue(
            any(tok in narrative for tok in ('kiš', 'pljus', 'padavin')),
            narrative)


if __name__ == '__main__':
    unittest.main(verbosity=2)
