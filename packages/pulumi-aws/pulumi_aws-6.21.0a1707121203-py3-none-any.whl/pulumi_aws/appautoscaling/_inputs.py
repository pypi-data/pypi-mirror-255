# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'PolicyStepScalingPolicyConfigurationArgs',
    'PolicyStepScalingPolicyConfigurationStepAdjustmentArgs',
    'PolicyTargetTrackingScalingPolicyConfigurationArgs',
    'PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationArgs',
    'PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationDimensionArgs',
    'PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricArgs',
    'PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatArgs',
    'PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricArgs',
    'PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricDimensionArgs',
    'PolicyTargetTrackingScalingPolicyConfigurationPredefinedMetricSpecificationArgs',
    'ScheduledActionScalableTargetActionArgs',
]

@pulumi.input_type
class PolicyStepScalingPolicyConfigurationArgs:
    def __init__(__self__, *,
                 adjustment_type: Optional[pulumi.Input[str]] = None,
                 cooldown: Optional[pulumi.Input[int]] = None,
                 metric_aggregation_type: Optional[pulumi.Input[str]] = None,
                 min_adjustment_magnitude: Optional[pulumi.Input[int]] = None,
                 step_adjustments: Optional[pulumi.Input[Sequence[pulumi.Input['PolicyStepScalingPolicyConfigurationStepAdjustmentArgs']]]] = None):
        """
        :param pulumi.Input[str] adjustment_type: Whether the adjustment is an absolute number or a percentage of the current capacity. Valid values are `ChangeInCapacity`, `ExactCapacity`, and `PercentChangeInCapacity`.
        :param pulumi.Input[int] cooldown: Amount of time, in seconds, after a scaling activity completes and before the next scaling activity can start.
        :param pulumi.Input[str] metric_aggregation_type: Aggregation type for the policy's metrics. Valid values are "Minimum", "Maximum", and "Average". Without a value, AWS will treat the aggregation type as "Average".
        :param pulumi.Input[int] min_adjustment_magnitude: Minimum number to adjust your scalable dimension as a result of a scaling activity. If the adjustment type is PercentChangeInCapacity, the scaling policy changes the scalable dimension of the scalable target by this amount.
        :param pulumi.Input[Sequence[pulumi.Input['PolicyStepScalingPolicyConfigurationStepAdjustmentArgs']]] step_adjustments: Set of adjustments that manage scaling. These have the following structure:
               
               ```python
               import pulumi
               import pulumi_aws as aws
               
               ecs_policy = aws.appautoscaling.Policy("ecsPolicy", step_scaling_policy_configuration=aws.appautoscaling.PolicyStepScalingPolicyConfigurationArgs(
                   step_adjustments=[
                       aws.appautoscaling.PolicyStepScalingPolicyConfigurationStepAdjustmentArgs(
                           metric_interval_lower_bound="1",
                           metric_interval_upper_bound="2",
                           scaling_adjustment=-1,
                       ),
                       aws.appautoscaling.PolicyStepScalingPolicyConfigurationStepAdjustmentArgs(
                           metric_interval_lower_bound="2",
                           metric_interval_upper_bound="3",
                           scaling_adjustment=1,
                       ),
                   ],
               ))
               ```
        """
        if adjustment_type is not None:
            pulumi.set(__self__, "adjustment_type", adjustment_type)
        if cooldown is not None:
            pulumi.set(__self__, "cooldown", cooldown)
        if metric_aggregation_type is not None:
            pulumi.set(__self__, "metric_aggregation_type", metric_aggregation_type)
        if min_adjustment_magnitude is not None:
            pulumi.set(__self__, "min_adjustment_magnitude", min_adjustment_magnitude)
        if step_adjustments is not None:
            pulumi.set(__self__, "step_adjustments", step_adjustments)

    @property
    @pulumi.getter(name="adjustmentType")
    def adjustment_type(self) -> Optional[pulumi.Input[str]]:
        """
        Whether the adjustment is an absolute number or a percentage of the current capacity. Valid values are `ChangeInCapacity`, `ExactCapacity`, and `PercentChangeInCapacity`.
        """
        return pulumi.get(self, "adjustment_type")

    @adjustment_type.setter
    def adjustment_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "adjustment_type", value)

    @property
    @pulumi.getter
    def cooldown(self) -> Optional[pulumi.Input[int]]:
        """
        Amount of time, in seconds, after a scaling activity completes and before the next scaling activity can start.
        """
        return pulumi.get(self, "cooldown")

    @cooldown.setter
    def cooldown(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "cooldown", value)

    @property
    @pulumi.getter(name="metricAggregationType")
    def metric_aggregation_type(self) -> Optional[pulumi.Input[str]]:
        """
        Aggregation type for the policy's metrics. Valid values are "Minimum", "Maximum", and "Average". Without a value, AWS will treat the aggregation type as "Average".
        """
        return pulumi.get(self, "metric_aggregation_type")

    @metric_aggregation_type.setter
    def metric_aggregation_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "metric_aggregation_type", value)

    @property
    @pulumi.getter(name="minAdjustmentMagnitude")
    def min_adjustment_magnitude(self) -> Optional[pulumi.Input[int]]:
        """
        Minimum number to adjust your scalable dimension as a result of a scaling activity. If the adjustment type is PercentChangeInCapacity, the scaling policy changes the scalable dimension of the scalable target by this amount.
        """
        return pulumi.get(self, "min_adjustment_magnitude")

    @min_adjustment_magnitude.setter
    def min_adjustment_magnitude(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "min_adjustment_magnitude", value)

    @property
    @pulumi.getter(name="stepAdjustments")
    def step_adjustments(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['PolicyStepScalingPolicyConfigurationStepAdjustmentArgs']]]]:
        """
        Set of adjustments that manage scaling. These have the following structure:

        ```python
        import pulumi
        import pulumi_aws as aws

        ecs_policy = aws.appautoscaling.Policy("ecsPolicy", step_scaling_policy_configuration=aws.appautoscaling.PolicyStepScalingPolicyConfigurationArgs(
            step_adjustments=[
                aws.appautoscaling.PolicyStepScalingPolicyConfigurationStepAdjustmentArgs(
                    metric_interval_lower_bound="1",
                    metric_interval_upper_bound="2",
                    scaling_adjustment=-1,
                ),
                aws.appautoscaling.PolicyStepScalingPolicyConfigurationStepAdjustmentArgs(
                    metric_interval_lower_bound="2",
                    metric_interval_upper_bound="3",
                    scaling_adjustment=1,
                ),
            ],
        ))
        ```
        """
        return pulumi.get(self, "step_adjustments")

    @step_adjustments.setter
    def step_adjustments(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['PolicyStepScalingPolicyConfigurationStepAdjustmentArgs']]]]):
        pulumi.set(self, "step_adjustments", value)


@pulumi.input_type
class PolicyStepScalingPolicyConfigurationStepAdjustmentArgs:
    def __init__(__self__, *,
                 scaling_adjustment: pulumi.Input[int],
                 metric_interval_lower_bound: Optional[pulumi.Input[str]] = None,
                 metric_interval_upper_bound: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[int] scaling_adjustment: Number of members by which to scale, when the adjustment bounds are breached. A positive value scales up. A negative value scales down.
        :param pulumi.Input[str] metric_interval_lower_bound: Lower bound for the difference between the alarm threshold and the CloudWatch metric. Without a value, AWS will treat this bound as negative infinity.
        :param pulumi.Input[str] metric_interval_upper_bound: Upper bound for the difference between the alarm threshold and the CloudWatch metric. Without a value, AWS will treat this bound as infinity. The upper bound must be greater than the lower bound.
        """
        pulumi.set(__self__, "scaling_adjustment", scaling_adjustment)
        if metric_interval_lower_bound is not None:
            pulumi.set(__self__, "metric_interval_lower_bound", metric_interval_lower_bound)
        if metric_interval_upper_bound is not None:
            pulumi.set(__self__, "metric_interval_upper_bound", metric_interval_upper_bound)

    @property
    @pulumi.getter(name="scalingAdjustment")
    def scaling_adjustment(self) -> pulumi.Input[int]:
        """
        Number of members by which to scale, when the adjustment bounds are breached. A positive value scales up. A negative value scales down.
        """
        return pulumi.get(self, "scaling_adjustment")

    @scaling_adjustment.setter
    def scaling_adjustment(self, value: pulumi.Input[int]):
        pulumi.set(self, "scaling_adjustment", value)

    @property
    @pulumi.getter(name="metricIntervalLowerBound")
    def metric_interval_lower_bound(self) -> Optional[pulumi.Input[str]]:
        """
        Lower bound for the difference between the alarm threshold and the CloudWatch metric. Without a value, AWS will treat this bound as negative infinity.
        """
        return pulumi.get(self, "metric_interval_lower_bound")

    @metric_interval_lower_bound.setter
    def metric_interval_lower_bound(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "metric_interval_lower_bound", value)

    @property
    @pulumi.getter(name="metricIntervalUpperBound")
    def metric_interval_upper_bound(self) -> Optional[pulumi.Input[str]]:
        """
        Upper bound for the difference between the alarm threshold and the CloudWatch metric. Without a value, AWS will treat this bound as infinity. The upper bound must be greater than the lower bound.
        """
        return pulumi.get(self, "metric_interval_upper_bound")

    @metric_interval_upper_bound.setter
    def metric_interval_upper_bound(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "metric_interval_upper_bound", value)


@pulumi.input_type
class PolicyTargetTrackingScalingPolicyConfigurationArgs:
    def __init__(__self__, *,
                 target_value: pulumi.Input[float],
                 customized_metric_specification: Optional[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationArgs']] = None,
                 disable_scale_in: Optional[pulumi.Input[bool]] = None,
                 predefined_metric_specification: Optional[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationPredefinedMetricSpecificationArgs']] = None,
                 scale_in_cooldown: Optional[pulumi.Input[int]] = None,
                 scale_out_cooldown: Optional[pulumi.Input[int]] = None):
        """
        :param pulumi.Input[float] target_value: Target value for the metric.
        :param pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationArgs'] customized_metric_specification: Custom CloudWatch metric. Documentation can be found  at: [AWS Customized Metric Specification](https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_CustomizedMetricSpecification.html). See supported fields below.
        :param pulumi.Input[bool] disable_scale_in: Whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. The default value is `false`.
        :param pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationPredefinedMetricSpecificationArgs'] predefined_metric_specification: Predefined metric. See supported fields below.
        :param pulumi.Input[int] scale_in_cooldown: Amount of time, in seconds, after a scale in activity completes before another scale in activity can start.
        :param pulumi.Input[int] scale_out_cooldown: Amount of time, in seconds, after a scale out activity completes before another scale out activity can start.
        """
        pulumi.set(__self__, "target_value", target_value)
        if customized_metric_specification is not None:
            pulumi.set(__self__, "customized_metric_specification", customized_metric_specification)
        if disable_scale_in is not None:
            pulumi.set(__self__, "disable_scale_in", disable_scale_in)
        if predefined_metric_specification is not None:
            pulumi.set(__self__, "predefined_metric_specification", predefined_metric_specification)
        if scale_in_cooldown is not None:
            pulumi.set(__self__, "scale_in_cooldown", scale_in_cooldown)
        if scale_out_cooldown is not None:
            pulumi.set(__self__, "scale_out_cooldown", scale_out_cooldown)

    @property
    @pulumi.getter(name="targetValue")
    def target_value(self) -> pulumi.Input[float]:
        """
        Target value for the metric.
        """
        return pulumi.get(self, "target_value")

    @target_value.setter
    def target_value(self, value: pulumi.Input[float]):
        pulumi.set(self, "target_value", value)

    @property
    @pulumi.getter(name="customizedMetricSpecification")
    def customized_metric_specification(self) -> Optional[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationArgs']]:
        """
        Custom CloudWatch metric. Documentation can be found  at: [AWS Customized Metric Specification](https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_CustomizedMetricSpecification.html). See supported fields below.
        """
        return pulumi.get(self, "customized_metric_specification")

    @customized_metric_specification.setter
    def customized_metric_specification(self, value: Optional[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationArgs']]):
        pulumi.set(self, "customized_metric_specification", value)

    @property
    @pulumi.getter(name="disableScaleIn")
    def disable_scale_in(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether scale in by the target tracking policy is disabled. If the value is true, scale in is disabled and the target tracking policy won't remove capacity from the scalable resource. Otherwise, scale in is enabled and the target tracking policy can remove capacity from the scalable resource. The default value is `false`.
        """
        return pulumi.get(self, "disable_scale_in")

    @disable_scale_in.setter
    def disable_scale_in(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "disable_scale_in", value)

    @property
    @pulumi.getter(name="predefinedMetricSpecification")
    def predefined_metric_specification(self) -> Optional[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationPredefinedMetricSpecificationArgs']]:
        """
        Predefined metric. See supported fields below.
        """
        return pulumi.get(self, "predefined_metric_specification")

    @predefined_metric_specification.setter
    def predefined_metric_specification(self, value: Optional[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationPredefinedMetricSpecificationArgs']]):
        pulumi.set(self, "predefined_metric_specification", value)

    @property
    @pulumi.getter(name="scaleInCooldown")
    def scale_in_cooldown(self) -> Optional[pulumi.Input[int]]:
        """
        Amount of time, in seconds, after a scale in activity completes before another scale in activity can start.
        """
        return pulumi.get(self, "scale_in_cooldown")

    @scale_in_cooldown.setter
    def scale_in_cooldown(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "scale_in_cooldown", value)

    @property
    @pulumi.getter(name="scaleOutCooldown")
    def scale_out_cooldown(self) -> Optional[pulumi.Input[int]]:
        """
        Amount of time, in seconds, after a scale out activity completes before another scale out activity can start.
        """
        return pulumi.get(self, "scale_out_cooldown")

    @scale_out_cooldown.setter
    def scale_out_cooldown(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "scale_out_cooldown", value)


@pulumi.input_type
class PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationArgs:
    def __init__(__self__, *,
                 dimensions: Optional[pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationDimensionArgs']]]] = None,
                 metric_name: Optional[pulumi.Input[str]] = None,
                 metrics: Optional[pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricArgs']]]] = None,
                 namespace: Optional[pulumi.Input[str]] = None,
                 statistic: Optional[pulumi.Input[str]] = None,
                 unit: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationDimensionArgs']]] dimensions: Dimensions of the metric.
        :param pulumi.Input[str] metric_name: Name of the metric.
        :param pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricArgs']]] metrics: Metrics to include, as a metric data query.
        :param pulumi.Input[str] namespace: Namespace of the metric.
        :param pulumi.Input[str] statistic: Statistic of the metric. Valid values: `Average`, `Minimum`, `Maximum`, `SampleCount`, and `Sum`.
        :param pulumi.Input[str] unit: Unit of the metrics to return.
        """
        if dimensions is not None:
            pulumi.set(__self__, "dimensions", dimensions)
        if metric_name is not None:
            pulumi.set(__self__, "metric_name", metric_name)
        if metrics is not None:
            pulumi.set(__self__, "metrics", metrics)
        if namespace is not None:
            pulumi.set(__self__, "namespace", namespace)
        if statistic is not None:
            pulumi.set(__self__, "statistic", statistic)
        if unit is not None:
            pulumi.set(__self__, "unit", unit)

    @property
    @pulumi.getter
    def dimensions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationDimensionArgs']]]]:
        """
        Dimensions of the metric.
        """
        return pulumi.get(self, "dimensions")

    @dimensions.setter
    def dimensions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationDimensionArgs']]]]):
        pulumi.set(self, "dimensions", value)

    @property
    @pulumi.getter(name="metricName")
    def metric_name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the metric.
        """
        return pulumi.get(self, "metric_name")

    @metric_name.setter
    def metric_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "metric_name", value)

    @property
    @pulumi.getter
    def metrics(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricArgs']]]]:
        """
        Metrics to include, as a metric data query.
        """
        return pulumi.get(self, "metrics")

    @metrics.setter
    def metrics(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricArgs']]]]):
        pulumi.set(self, "metrics", value)

    @property
    @pulumi.getter
    def namespace(self) -> Optional[pulumi.Input[str]]:
        """
        Namespace of the metric.
        """
        return pulumi.get(self, "namespace")

    @namespace.setter
    def namespace(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "namespace", value)

    @property
    @pulumi.getter
    def statistic(self) -> Optional[pulumi.Input[str]]:
        """
        Statistic of the metric. Valid values: `Average`, `Minimum`, `Maximum`, `SampleCount`, and `Sum`.
        """
        return pulumi.get(self, "statistic")

    @statistic.setter
    def statistic(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "statistic", value)

    @property
    @pulumi.getter
    def unit(self) -> Optional[pulumi.Input[str]]:
        """
        Unit of the metrics to return.
        """
        return pulumi.get(self, "unit")

    @unit.setter
    def unit(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "unit", value)


@pulumi.input_type
class PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationDimensionArgs:
    def __init__(__self__, *,
                 name: pulumi.Input[str],
                 value: pulumi.Input[str]):
        """
        :param pulumi.Input[str] name: Name of the policy. Must be between 1 and 255 characters in length.
        :param pulumi.Input[str] value: Value of the dimension.
        """
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def name(self) -> pulumi.Input[str]:
        """
        Name of the policy. Must be between 1 and 255 characters in length.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: pulumi.Input[str]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def value(self) -> pulumi.Input[str]:
        """
        Value of the dimension.
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: pulumi.Input[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricArgs:
    def __init__(__self__, *,
                 id: pulumi.Input[str],
                 expression: Optional[pulumi.Input[str]] = None,
                 label: Optional[pulumi.Input[str]] = None,
                 metric_stat: Optional[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatArgs']] = None,
                 return_data: Optional[pulumi.Input[bool]] = None):
        """
        :param pulumi.Input[str] id: Short name for the metric used in target tracking scaling policy.
        :param pulumi.Input[str] expression: Math expression used on the returned metric. You must specify either `expression` or `metric_stat`, but not both.
        :param pulumi.Input[str] label: Human-readable label for this metric or expression.
        :param pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatArgs'] metric_stat: Structure that defines CloudWatch metric to be used in target tracking scaling policy. You must specify either `expression` or `metric_stat`, but not both.
        :param pulumi.Input[bool] return_data: Boolean that indicates whether to return the timestamps and raw data values of this metric, the default is true
        """
        pulumi.set(__self__, "id", id)
        if expression is not None:
            pulumi.set(__self__, "expression", expression)
        if label is not None:
            pulumi.set(__self__, "label", label)
        if metric_stat is not None:
            pulumi.set(__self__, "metric_stat", metric_stat)
        if return_data is not None:
            pulumi.set(__self__, "return_data", return_data)

    @property
    @pulumi.getter
    def id(self) -> pulumi.Input[str]:
        """
        Short name for the metric used in target tracking scaling policy.
        """
        return pulumi.get(self, "id")

    @id.setter
    def id(self, value: pulumi.Input[str]):
        pulumi.set(self, "id", value)

    @property
    @pulumi.getter
    def expression(self) -> Optional[pulumi.Input[str]]:
        """
        Math expression used on the returned metric. You must specify either `expression` or `metric_stat`, but not both.
        """
        return pulumi.get(self, "expression")

    @expression.setter
    def expression(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "expression", value)

    @property
    @pulumi.getter
    def label(self) -> Optional[pulumi.Input[str]]:
        """
        Human-readable label for this metric or expression.
        """
        return pulumi.get(self, "label")

    @label.setter
    def label(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "label", value)

    @property
    @pulumi.getter(name="metricStat")
    def metric_stat(self) -> Optional[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatArgs']]:
        """
        Structure that defines CloudWatch metric to be used in target tracking scaling policy. You must specify either `expression` or `metric_stat`, but not both.
        """
        return pulumi.get(self, "metric_stat")

    @metric_stat.setter
    def metric_stat(self, value: Optional[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatArgs']]):
        pulumi.set(self, "metric_stat", value)

    @property
    @pulumi.getter(name="returnData")
    def return_data(self) -> Optional[pulumi.Input[bool]]:
        """
        Boolean that indicates whether to return the timestamps and raw data values of this metric, the default is true
        """
        return pulumi.get(self, "return_data")

    @return_data.setter
    def return_data(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "return_data", value)


@pulumi.input_type
class PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatArgs:
    def __init__(__self__, *,
                 metric: pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricArgs'],
                 stat: pulumi.Input[str],
                 unit: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricArgs'] metric: Structure that defines the CloudWatch metric to return, including the metric name, namespace, and dimensions.
        :param pulumi.Input[str] stat: Statistic of the metrics to return.
        :param pulumi.Input[str] unit: Unit of the metrics to return.
        """
        pulumi.set(__self__, "metric", metric)
        pulumi.set(__self__, "stat", stat)
        if unit is not None:
            pulumi.set(__self__, "unit", unit)

    @property
    @pulumi.getter
    def metric(self) -> pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricArgs']:
        """
        Structure that defines the CloudWatch metric to return, including the metric name, namespace, and dimensions.
        """
        return pulumi.get(self, "metric")

    @metric.setter
    def metric(self, value: pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricArgs']):
        pulumi.set(self, "metric", value)

    @property
    @pulumi.getter
    def stat(self) -> pulumi.Input[str]:
        """
        Statistic of the metrics to return.
        """
        return pulumi.get(self, "stat")

    @stat.setter
    def stat(self, value: pulumi.Input[str]):
        pulumi.set(self, "stat", value)

    @property
    @pulumi.getter
    def unit(self) -> Optional[pulumi.Input[str]]:
        """
        Unit of the metrics to return.
        """
        return pulumi.get(self, "unit")

    @unit.setter
    def unit(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "unit", value)


@pulumi.input_type
class PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricArgs:
    def __init__(__self__, *,
                 metric_name: pulumi.Input[str],
                 namespace: pulumi.Input[str],
                 dimensions: Optional[pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricDimensionArgs']]]] = None):
        """
        :param pulumi.Input[str] metric_name: Name of the metric.
        :param pulumi.Input[str] namespace: Namespace of the metric.
        :param pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricDimensionArgs']]] dimensions: Dimensions of the metric.
        """
        pulumi.set(__self__, "metric_name", metric_name)
        pulumi.set(__self__, "namespace", namespace)
        if dimensions is not None:
            pulumi.set(__self__, "dimensions", dimensions)

    @property
    @pulumi.getter(name="metricName")
    def metric_name(self) -> pulumi.Input[str]:
        """
        Name of the metric.
        """
        return pulumi.get(self, "metric_name")

    @metric_name.setter
    def metric_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "metric_name", value)

    @property
    @pulumi.getter
    def namespace(self) -> pulumi.Input[str]:
        """
        Namespace of the metric.
        """
        return pulumi.get(self, "namespace")

    @namespace.setter
    def namespace(self, value: pulumi.Input[str]):
        pulumi.set(self, "namespace", value)

    @property
    @pulumi.getter
    def dimensions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricDimensionArgs']]]]:
        """
        Dimensions of the metric.
        """
        return pulumi.get(self, "dimensions")

    @dimensions.setter
    def dimensions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricDimensionArgs']]]]):
        pulumi.set(self, "dimensions", value)


@pulumi.input_type
class PolicyTargetTrackingScalingPolicyConfigurationCustomizedMetricSpecificationMetricMetricStatMetricDimensionArgs:
    def __init__(__self__, *,
                 name: pulumi.Input[str],
                 value: pulumi.Input[str]):
        """
        :param pulumi.Input[str] name: Name of the policy. Must be between 1 and 255 characters in length.
        :param pulumi.Input[str] value: Value of the dimension.
        """
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def name(self) -> pulumi.Input[str]:
        """
        Name of the policy. Must be between 1 and 255 characters in length.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: pulumi.Input[str]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def value(self) -> pulumi.Input[str]:
        """
        Value of the dimension.
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: pulumi.Input[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class PolicyTargetTrackingScalingPolicyConfigurationPredefinedMetricSpecificationArgs:
    def __init__(__self__, *,
                 predefined_metric_type: pulumi.Input[str],
                 resource_label: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] predefined_metric_type: Metric type.
        :param pulumi.Input[str] resource_label: Reserved for future use if the `predefined_metric_type` is not `ALBRequestCountPerTarget`. If the `predefined_metric_type` is `ALBRequestCountPerTarget`, you must specify this argument. Documentation can be found at: [AWS Predefined Scaling Metric Specification](https://docs.aws.amazon.com/autoscaling/plans/APIReference/API_PredefinedScalingMetricSpecification.html). Must be less than or equal to 1023 characters in length.
        """
        pulumi.set(__self__, "predefined_metric_type", predefined_metric_type)
        if resource_label is not None:
            pulumi.set(__self__, "resource_label", resource_label)

    @property
    @pulumi.getter(name="predefinedMetricType")
    def predefined_metric_type(self) -> pulumi.Input[str]:
        """
        Metric type.
        """
        return pulumi.get(self, "predefined_metric_type")

    @predefined_metric_type.setter
    def predefined_metric_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "predefined_metric_type", value)

    @property
    @pulumi.getter(name="resourceLabel")
    def resource_label(self) -> Optional[pulumi.Input[str]]:
        """
        Reserved for future use if the `predefined_metric_type` is not `ALBRequestCountPerTarget`. If the `predefined_metric_type` is `ALBRequestCountPerTarget`, you must specify this argument. Documentation can be found at: [AWS Predefined Scaling Metric Specification](https://docs.aws.amazon.com/autoscaling/plans/APIReference/API_PredefinedScalingMetricSpecification.html). Must be less than or equal to 1023 characters in length.
        """
        return pulumi.get(self, "resource_label")

    @resource_label.setter
    def resource_label(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_label", value)


@pulumi.input_type
class ScheduledActionScalableTargetActionArgs:
    def __init__(__self__, *,
                 max_capacity: Optional[pulumi.Input[int]] = None,
                 min_capacity: Optional[pulumi.Input[int]] = None):
        """
        :param pulumi.Input[int] max_capacity: Maximum capacity. At least one of `max_capacity` or `min_capacity` must be set.
        :param pulumi.Input[int] min_capacity: Minimum capacity. At least one of `min_capacity` or `max_capacity` must be set.
        """
        if max_capacity is not None:
            pulumi.set(__self__, "max_capacity", max_capacity)
        if min_capacity is not None:
            pulumi.set(__self__, "min_capacity", min_capacity)

    @property
    @pulumi.getter(name="maxCapacity")
    def max_capacity(self) -> Optional[pulumi.Input[int]]:
        """
        Maximum capacity. At least one of `max_capacity` or `min_capacity` must be set.
        """
        return pulumi.get(self, "max_capacity")

    @max_capacity.setter
    def max_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "max_capacity", value)

    @property
    @pulumi.getter(name="minCapacity")
    def min_capacity(self) -> Optional[pulumi.Input[int]]:
        """
        Minimum capacity. At least one of `min_capacity` or `max_capacity` must be set.
        """
        return pulumi.get(self, "min_capacity")

    @min_capacity.setter
    def min_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "min_capacity", value)


