"""
Django management command for A/B test statistical analysis.

Performs two-proportion z-test and provides executive summary.

Usage:
    python manage.py ab_analyze_button_label --experiment=button_label_kudos_vs_thanks
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from core.models import ABTestEvent
import math


class Command(BaseCommand):
    help = 'Perform statistical analysis of A/B test button label experiment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--experiment',
            type=str,
            default='button_label_kudos_vs_thanks',
            help='Experiment name to analyze (default: button_label_kudos_vs_thanks)',
        )
        parser.add_argument(
            '--exclude-forced',
            action='store_true',
            help='Exclude forced variants (from ?force_variant parameter)',
        )
        parser.add_argument(
            '--confidence-level',
            type=float,
            default=0.95,
            help='Confidence level for intervals (default: 0.95 for 95%%)',
        )

    def handle(self, *args, **options):
        experiment_name = options['experiment']
        exclude_forced = options['exclude_forced']
        confidence_level = options['confidence_level']

        self.stdout.write(self.style.SUCCESS('\n=== A/B Test Statistical Analysis ==='))
        self.stdout.write(f'Experiment: {experiment_name}')
        self.stdout.write(f'Confidence Level: {confidence_level * 100:.1f}%')
        if exclude_forced:
            self.stdout.write('Excluding forced variants from analysis')
        self.stdout.write('')

        # ====================================================================
        # 1. HYPOTHESES SECTION
        # ====================================================================
        self.stdout.write('HYPOTHESES:')
        self.stdout.write('-' * 70)
        self.stdout.write('Null Hypothesis (H₀):')
        self.stdout.write('  Changing the label from "kudos" to "thanks" has no effect on the button click rate.')
        self.stdout.write('')
        self.stdout.write('Alternative Hypothesis (H₁):')
        self.stdout.write('  The "thanks" label changes the button click rate (higher or lower) compared to "kudos".')
        self.stdout.write('-' * 70)
        self.stdout.write('')

        # ====================================================================
        # 2. DATA AGGREGATION
        # ====================================================================
        # Build query
        exposure_query = Q(experiment_name=experiment_name, event_type='exposure')
        conversion_query = Q(experiment_name=experiment_name, event_type='conversion')
        
        if exclude_forced:
            exposure_query &= Q(is_forced=False)
            conversion_query &= Q(is_forced=False)

        # Get exposure and conversion counts per variant
        exposure_counts = (
            ABTestEvent.objects
            .filter(exposure_query)
            .values('variant')
            .annotate(count=Count('id'))
        )
        
        conversion_counts = (
            ABTestEvent.objects
            .filter(conversion_query)
            .values('variant')
            .annotate(count=Count('id'))
        )

        exposure_dict = {item['variant']: item['count'] for item in exposure_counts}
        conversion_dict = {item['variant']: item['count'] for item in conversion_counts}

        # Get all variants
        all_variants = sorted(set(list(exposure_dict.keys()) + list(conversion_dict.keys())))
        
        if len(all_variants) != 2:
            self.stdout.write(
                self.style.ERROR(
                    f'ERROR: Expected exactly 2 variants, found {len(all_variants)}: {all_variants}'
                )
            )
            self.stdout.write('')
            self.stdout.write('This could happen if:')
            self.stdout.write('  - Not enough data has been collected yet')
            self.stdout.write('  - The experiment name is incorrect')
            self.stdout.write('  - Events have not been logged properly')
            self.stdout.write('')
            self.stdout.write('Please check that:')
            self.stdout.write('  1. The A/B test endpoint has received traffic')
            self.stdout.write('  2. Both variants have been shown to users')
            self.stdout.write('  3. The experiment name matches: button_label_kudos_vs_thanks')
            return

        variant_a = 'kudos'  # Variant A
        variant_b = 'thanks'  # Variant B

        # Ensure both variants are present
        if variant_a not in all_variants or variant_b not in all_variants:
            self.stdout.write(
                self.style.ERROR(
                    f'ERROR: Missing expected variants. Found: {all_variants}, '
                    f'Expected: ["{variant_a}", "{variant_b}"]'
                )
            )
            return

        # Get counts per variant (nA, cA, pA, nB, cB, pB)
        nA = exposure_dict.get(variant_a, 0)  # exposures for variant A
        cA = conversion_dict.get(variant_a, 0)  # conversions for variant A
        pA = cA / nA if nA > 0 else 0  # conversion rate for variant A

        nB = exposure_dict.get(variant_b, 0)  # exposures for variant B
        cB = conversion_dict.get(variant_b, 0)  # conversions for variant B
        pB = cB / nB if nB > 0 else 0  # conversion rate for variant B

        # Check for sufficient data
        if nA == 0 or nB == 0:
            self.stdout.write(
                self.style.WARNING('WARNING: Insufficient data.')
            )
            self.stdout.write(f'  Variant A ("{variant_a}"): {nA} exposures')
            self.stdout.write(f'  Variant B ("{variant_b}"): {nB} exposures')
            self.stdout.write('')
            self.stdout.write('Please collect more data before running the analysis.')
            return

        # ====================================================================
        # 3. NUMERICAL RESULTS
        # ====================================================================
        self.stdout.write('NUMERICAL RESULTS:')
        self.stdout.write('-' * 70)
        self.stdout.write(f'Variant A ("{variant_a}"):')
        self.stdout.write(f'  Exposures (nA):     {nA:,}')
        self.stdout.write(f'  Conversions (cA):   {cA:,}')
        self.stdout.write(f'  Conversion Rate:    {pA*100:.4f}% ({pA:.6f})')
        self.stdout.write('')
        self.stdout.write(f'Variant B ("{variant_b}"):')
        self.stdout.write(f'  Exposures (nB):     {nB:,}')
        self.stdout.write(f'  Conversions (cB):   {cB:,}')
        self.stdout.write(f'  Conversion Rate:    {pB*100:.4f}% ({pB:.6f})')
        self.stdout.write('')

        # Effect size (difference in conversion rates)
        effect_size = pB - pA  # B minus A
        relative_improvement = ((pB - pA) / pA * 100) if pA > 0 else 0

        self.stdout.write('Effect Size:')
        self.stdout.write(f'  Absolute Difference (pB - pA): {effect_size*100:+.4f} percentage points')
        if pA > 0:
            self.stdout.write(f'  Relative Improvement:        {relative_improvement:+.2f}%')
        self.stdout.write('')

        # ====================================================================
        # 4. STATISTICAL TEST (Two-Proportion Z-Test)
        # ====================================================================
        # Pooled proportion
        p_pooled = (cA + cB) / (nA + nB)
        
        # Standard error under null hypothesis (pooled)
        se_pooled = math.sqrt(p_pooled * (1 - p_pooled) * (1/nA + 1/nB))
        
        if se_pooled == 0:
            self.stdout.write(
                self.style.ERROR('ERROR: Cannot calculate statistics. Standard error is zero.')
            )
            return

        # Z-score
        z_score = (pB - pA) / se_pooled

        # P-value (two-tailed test)
        def norm_cdf(x):
            """Approximate standard normal CDF using error function."""
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        
        p_value = 2 * (1 - norm_cdf(abs(z_score)))

        # Confidence interval for difference in proportions
        se_diff = math.sqrt((pA * (1 - pA) / nA) + (pB * (1 - pB) / nB))
        
        # Z-critical value for confidence level
        def norm_ppf(p):
            """Approximate inverse standard normal CDF."""
            lookup = {
                0.90: 1.64485,
                0.95: 1.95996,
                0.99: 2.57583,
            }
            if p in lookup:
                return lookup[p]
            # Simple approximation for other values
            sign = 1 if p > 0.5 else -1
            p_adj = p if p <= 0.5 else 1 - p
            t = math.sqrt(-2 * math.log(p_adj))
            return sign * (t - (0.010328 * t + 0.802853) * t / (1 + 1.432788 * t + 0.189269 * t * t))
        
        z_critical = norm_ppf((1 + confidence_level) / 2)
        margin_error = z_critical * se_diff
        ci_lower = effect_size - margin_error
        ci_upper = effect_size + margin_error

        self.stdout.write('Statistical Test Results:')
        self.stdout.write(f'  Z-Score:                     {z_score:+.6f}')
        self.stdout.write(f'  P-Value (two-tailed):        {p_value:.6f}')
        self.stdout.write(
            f'  95% Confidence Interval:       [{ci_lower*100:+.4f}%, {ci_upper*100:+.4f}%]'
        )
        self.stdout.write('-' * 70)
        self.stdout.write('')

        # ====================================================================
        # 5. EXECUTIVE SUMMARY (Plain English)
        # ====================================================================
        self.stdout.write('EXECUTIVE SUMMARY:')
        self.stdout.write('-' * 70)
        
        alpha = 1 - confidence_level
        is_significant = p_value < alpha
        abs_effect = abs(effect_size) * 100
        abs_relative = abs(relative_improvement)

        if is_significant:
            if effect_size > 0:
                # Variant B (thanks) is significantly better
                self.stdout.write(
                    f'Variant B ("thanks") performs significantly better than Variant A ("kudos"), '
                    f'with an estimated +{abs_effect:.2f} percentage point lift in conversion '
                    f'(p = {p_value:.6f}, 95% CI [{ci_lower*100:+.2f}%, {ci_upper*100:+.2f}%]).'
                )
                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS(
                        'RECOMMENDATION: We recommend rolling out "thanks" to 100% of users for this button.'
                    )
                )
            else:
                # Variant A (kudos) is significantly better
                self.stdout.write(
                    f'Variant A ("kudos") performs significantly better than Variant B ("thanks"), '
                    f'with an estimated {abs_effect:.2f} percentage point higher conversion rate '
                    f'(p = {p_value:.6f}, 95% CI [{ci_lower*100:+.2f}%, {ci_upper*100:+.2f}%]).'
                )
                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS(
                        'RECOMMENDATION: We recommend keeping "kudos" for 100% of users for this button.'
                    )
                )
        else:
            # Not significant
            self.stdout.write(
                f'We did not find strong evidence that the label change impacts user behavior '
                f'(p = {p_value:.6f}, 95% CI [{ci_lower*100:+.2f}%, {ci_upper*100:+.2f}%]).'
            )
            self.stdout.write('')
            
            if abs_effect < 0.5:
                self.stdout.write(
                    'The observed difference is very small, suggesting the variants are effectively equivalent.'
                )
            elif abs_relative > 5:
                self.stdout.write(
                    self.style.WARNING(
                        f'NOTE: Despite non-significance, there is a notable observed difference '
                        f'({abs_relative:.1f}% relative change). Consider collecting more data to '
                        'increase statistical power.'
                    )
                )
            
            self.stdout.write('')
            self.stdout.write(
                'RECOMMENDATION: Either label is acceptable; choose based on branding or copy tone '
                'rather than performance.'
            )

        self.stdout.write('-' * 70)
        self.stdout.write('')

        # Sample size note
        min_sample = min(nA, nB)
        if min_sample < 100:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Sample Size Note: Small sample size ({min_sample} exposures per variant). '
                    'Results may be unreliable. Consider collecting more data for greater confidence.'
                )
            )
        elif min_sample < 1000:
            self.stdout.write(
                f'ℹ️  Sample Size: {min_sample} exposures per variant (moderate sample size).'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Sample Size: {min_sample} exposures per variant (good sample size).'
                )
            )

        self.stdout.write('')

