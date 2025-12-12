"""
Django management command for statistical A/B test analysis.

Calculates p-value, effect size, confidence intervals, and provides
executive/managerial interpretation.

Usage:
    python manage.py ab_analyze --experiment=button_label_kudos_vs_thanks
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from core.models import ABTestEvent
import math


class Command(BaseCommand):
    help = 'Perform statistical analysis of A/B test results'

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
        self.stdout.write(f'Exclude Forced: {exclude_forced}\n')

        # Build query
        exposure_query = Q(experiment_name=experiment_name, event_type='exposure')
        click_query = Q(experiment_name=experiment_name, event_type='click')
        
        if exclude_forced:
            exposure_query &= Q(is_forced=False)
            click_query &= Q(is_forced=False)

        # Get exposure and click counts per variant
        exposure_counts = (
            ABTestEvent.objects
            .filter(exposure_query)
            .values('variant')
            .annotate(count=Count('id'))
        )
        
        click_counts = (
            ABTestEvent.objects
            .filter(click_query)
            .values('variant')
            .annotate(count=Count('id'))
        )

        exposure_dict = {item['variant']: item['count'] for item in exposure_counts}
        click_dict = {item['variant']: item['count'] for item in click_counts}

        # Get all variants
        all_variants = sorted(set(list(exposure_dict.keys()) + list(click_dict.keys())))
        
        if len(all_variants) != 2:
            self.stdout.write(
                self.style.ERROR(
                    f'Expected exactly 2 variants, found {len(all_variants)}. '
                    'Cannot perform statistical analysis.'
                )
            )
            return

        variant_a = all_variants[0]
        variant_b = all_variants[1]

        # Get counts
        n_a = exposure_dict.get(variant_a, 0)
        n_b = exposure_dict.get(variant_b, 0)
        clicks_a = click_dict.get(variant_a, 0)
        clicks_b = click_dict.get(variant_b, 0)

        if n_a == 0 or n_b == 0:
            self.stdout.write(
                self.style.ERROR('Insufficient data: one or both variants have zero exposures.')
            )
            return

        # Calculate conversion rates
        p_a = clicks_a / n_a if n_a > 0 else 0
        p_b = clicks_b / n_b if n_b > 0 else 0

        # Display raw data
        self.stdout.write('Raw Data:')
        self.stdout.write('-' * 60)
        self.stdout.write(f'{variant_a:10s}: {clicks_a:6d} clicks / {n_a:6d} exposures = {p_a*100:5.2f}% conversion')
        self.stdout.write(f'{variant_b:10s}: {clicks_b:6d} clicks / {n_b:6d} exposures = {p_b*100:5.2f}% conversion')
        self.stdout.write('-' * 60)
        self.stdout.write('')

        # Statistical calculations
        # Two-proportion z-test
        p_pooled = (clicks_a + clicks_b) / (n_a + n_b)
        se_pooled = math.sqrt(p_pooled * (1 - p_pooled) * (1/n_a + 1/n_b))
        
        if se_pooled == 0:
            self.stdout.write(self.style.ERROR('Cannot calculate statistics: standard error is zero.'))
            return

        # Z-score
        z_score = (p_b - p_a) / se_pooled if se_pooled > 0 else 0

        # P-value (two-tailed test) using standard normal CDF approximation
        # Using error function approximation for normal CDF
        def norm_cdf(x):
            """Approximate standard normal CDF using error function."""
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        
        p_value = 2 * (1 - norm_cdf(abs(z_score)))

        # Effect size (Cohen's h for proportions)
        h = 2 * (math.asin(math.sqrt(p_b)) - math.asin(math.sqrt(p_a)))

        # Confidence interval for difference in proportions
        se_diff = math.sqrt((p_a * (1 - p_a) / n_a) + (p_b * (1 - p_b) / n_b))
        
        # Z-critical value for confidence level (using inverse normal CDF approximation)
        def norm_ppf(p):
            """Approximate inverse standard normal CDF (quantile function)."""
            # Approximation using Beasley-Springer-Moro algorithm (simplified)
            # For common confidence levels, use lookup table
            lookup = {
                0.90: 1.64485,
                0.95: 1.95996,
                0.99: 2.57583,
            }
            if p in lookup:
                return lookup[p]
            # Simple approximation for other values
            # Using Winitzki's approximation
            sign = 1 if p > 0.5 else -1
            p_adj = p if p <= 0.5 else 1 - p
            t = math.sqrt(-2 * math.log(p_adj))
            return sign * (t - (0.010328 * t + 0.802853) * t / (1 + 1.432788 * t + 0.189269 * t * t))
        
        z_critical = norm_ppf((1 + confidence_level) / 2)
        margin_error = z_critical * se_diff
        diff = p_b - p_a
        ci_lower = diff - margin_error
        ci_upper = diff + margin_error

        # Relative improvement
        relative_improvement = ((p_b - p_a) / p_a * 100) if p_a > 0 else 0

        # Display statistical results
        self.stdout.write('Statistical Results:')
        self.stdout.write('-' * 60)
        self.stdout.write(f'Difference (B - A):     {diff*100:+.2f} percentage points')
        self.stdout.write(f'Relative Improvement:  {relative_improvement:+.2f}%')
        self.stdout.write(f'Z-Score:               {z_score:+.4f}')
        self.stdout.write(f'P-Value:               {p_value:.6f}')
        self.stdout.write(f'Effect Size (Cohen\'s h): {h:+.4f}')
        self.stdout.write(
            f'Confidence Interval ({confidence_level*100:.1f}%): '
            f'[{ci_lower*100:+.2f}%, {ci_upper*100:+.2f}%]'
        )
        self.stdout.write('-' * 60)
        self.stdout.write('')

        # Interpretation
        self.stdout.write('Interpretation:')
        self.stdout.write('-' * 60)
        
        alpha = 1 - confidence_level
        is_significant = p_value < alpha
        
        if is_significant:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Statistically Significant (p < {alpha:.3f})'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'✗ Not Statistically Significant (p >= {alpha:.3f})'
                )
            )

        # Effect size interpretation
        abs_h = abs(h)
        if abs_h < 0.2:
            effect_size_desc = "negligible"
        elif abs_h < 0.5:
            effect_size_desc = "small"
        elif abs_h < 0.8:
            effect_size_desc = "medium"
        else:
            effect_size_desc = "large"
        
        self.stdout.write(f'Effect Size: {effect_size_desc} (|h| = {abs_h:.4f})')

        # Executive summary
        self.stdout.write('')
        self.stdout.write('Executive Summary:')
        self.stdout.write('-' * 60)
        
        if is_significant:
            winner = variant_b if p_b > p_a else variant_a
            loser = variant_a if winner == variant_b else variant_b
            winner_rate = p_b if winner == variant_b else p_a
            loser_rate = p_a if winner == variant_b else p_b
            improvement = abs(relative_improvement)
            
            self.stdout.write(
                f'• {winner.upper()} significantly outperforms {loser.upper()} '
                f'({winner_rate*100:.2f}% vs {loser_rate*100:.2f}% conversion rate)'
            )
            self.stdout.write(f'• Improvement: {improvement:.2f}% relative increase')
            self.stdout.write(
                f'• Confidence: We are {confidence_level*100:.0f}% confident the true '
                f'difference is between {ci_lower*100:+.2f}% and {ci_upper*100:+.2f}%'
            )
            self.stdout.write(f'• Recommendation: Deploy {winner.upper()} variant')
        else:
            self.stdout.write('• No statistically significant difference detected')
            self.stdout.write(
                f'• The observed difference ({diff*100:+.2f} percentage points) '
                'could be due to random chance'
            )
            self.stdout.write(
                '• Recommendation: Continue testing or consider that variants '
                'may be equivalent'
            )
            
            if abs(relative_improvement) > 5:
                self.stdout.write(
                    self.style.WARNING(
                        '  Note: Despite non-significance, there is a notable '
                        f'observed difference ({abs(relative_improvement):.1f}%). '
                        'Consider collecting more data.'
                    )
                )

        self.stdout.write('-' * 60)
        self.stdout.write('')

        # Sample size note
        min_sample = min(n_a, n_b)
        if min_sample < 100:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Warning: Small sample size ({min_sample} exposures per variant). '
                    'Results may be unreliable. Consider collecting more data.'
                )
            )
        elif min_sample < 1000:
            self.stdout.write(
                f'ℹ️  Sample size: {min_sample} exposures per variant (moderate)'
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Sample size: {min_sample} exposures per variant (good)'
                )
            )

        self.stdout.write('')

