import sgqlc.types
import sgqlc.types.datetime
import sgqlc.types.relay


schema = sgqlc.types.Schema()


# Unexport Node/PageInfo, let schema re-declare them
schema -= sgqlc.types.relay.Node
schema -= sgqlc.types.relay.PageInfo



########################################################################
# Scalars and Enumerations
########################################################################
class AccessDeniedReason(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CustomerIsArchived', 'CustomerNotFound', 'CustomerResourceNotFound', 'FeatureNotFound', 'NoActiveSubscription', 'NoFeatureEntitlementInSubscription', 'RequestedUsageExceedingLimit', 'Unknown')


class AccountStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ACTIVE', 'BLOCKED')


class AddonSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('billingId', 'createdAt', 'description', 'displayName', 'environmentId', 'id', 'isLatest', 'pricingType', 'productId', 'refId', 'status', 'updatedAt', 'versionNumber')


class AggregationFunction(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('AVG', 'COUNT', 'MAX', 'MIN', 'SUM', 'UNIQUE')


class Alignment(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CENTER', 'LEFT', 'RIGHT')


class ApiKeySortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('id',)


class ApiKeyType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CLIENT', 'SERVER')


class BillingAnchor(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('START_OF_THE_MONTH', 'SUBSCRIPTION_START')


class BillingModel(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('FLAT_FEE', 'PER_UNIT', 'USAGE_BASED')


class BillingPeriod(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ANNUALLY', 'MONTHLY')


class BillingVendorIdentifier(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('STRIPE',)


Boolean = sgqlc.types.Boolean

class ChangeType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ADDED', 'DELETED', 'MODIFIED', 'REORDERED')


class ConditionOperation(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('EQUALS', 'GREATER_THAN', 'GREATER_THAN_OR_EQUAL', 'IS_NOT_NULL', 'IS_NULL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'NOT_EQUALS')


class ConnectionCursor(sgqlc.types.Scalar):
    __schema__ = schema


class CouponSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('billingId', 'createdAt', 'description', 'environmentId', 'id', 'name', 'refId', 'status', 'type', 'updatedAt')


class CouponStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ACTIVE', 'ARCHIVED')


class CouponType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('FIXED', 'PERCENTAGE')


class Currency(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('AED', 'ALL', 'AMD', 'ANG', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BIF', 'BMD', 'BND', 'BSD', 'BWP', 'BYN', 'BZD', 'CAD', 'CDF', 'CHF', 'CLP', 'CNY', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EGP', 'ETB', 'EUR', 'FJD', 'GBP', 'GEL', 'GIP', 'GMD', 'GNF', 'GYD', 'HKD', 'HRK', 'HTG', 'IDR', 'ILS', 'INR', 'ISK', 'JMD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KRW', 'KYD', 'KZT', 'LBP', 'LKR', 'LRD', 'LSL', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRO', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NOK', 'NPR', 'NZD', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SEK', 'SGD', 'SLE', 'SLL', 'SOS', 'SZL', 'THB', 'TJS', 'TOP', 'TRY', 'TTD', 'TZS', 'UAH', 'UGX', 'USD', 'UZS', 'VND', 'VUV', 'WST', 'XAF', 'XCD', 'XOF', 'XPF', 'YER', 'ZAR', 'ZMW')


class CustomerResourceSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'environmentId', 'resourceId')


class CustomerSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('billingId', 'createdAt', 'crmHubspotCompanyId', 'crmHubspotCompanyUrl', 'crmId', 'customerId', 'deletedAt', 'email', 'environmentId', 'id', 'name', 'refId', 'searchQuery', 'updatedAt')


class CustomerSubscriptionSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('billingId', 'cancelReason', 'cancellationDate', 'createdAt', 'crmId', 'crmLinkUrl', 'currentBillingPeriodEnd', 'currentBillingPeriodStart', 'effectiveEndDate', 'endDate', 'environmentId', 'id', 'oldBillingId', 'paymentCollection', 'pricingType', 'refId', 'resourceId', 'startDate', 'status', 'subscriptionId', 'trialEndDate')


DateTime = sgqlc.types.datetime.DateTime

class Department(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CEO_OR_FOUNDER', 'ENGINEERING', 'GROWTH', 'MARKETING', 'MONETIZATION', 'OTHER', 'PRODUCT')


class DiscountDurationType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('FOREVER', 'ONCE', 'REPEATING')


class DiscountType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('FIXED', 'PERCENTAGE')


class EntitlementResetPeriod(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('DAY', 'HOUR', 'MONTH', 'WEEK', 'YEAR')


class EntitySelectionMode(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('BLACK_LIST', 'WHITE_LIST')


class EnvironmentProvisionStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('DONE', 'FAILED', 'IN_PROGRESS', 'NOT_PROVISIONED')


class EnvironmentSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'displayName', 'id', 'permanentDeletionDate', 'slug')


class EnvironmentType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('DEVELOPMENT', 'PRODUCTION', 'SANDBOX')


class ErrorCode(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('AccountNotFoundError', 'AddonHasToHavePriceError', 'AddonNotFound', 'AddonWithDraftCannotBeDeletedError', 'AmountTooLarge', 'ArchivedCouponCantBeApplied', 'AuthCustomerMismatch', 'AwsMarketplaceIntegrationError', 'AwsMarketplaceIntegrationValidationError', 'BadUserInput', 'BillingPeriodMissingError', 'CannotArchiveFeatureError', 'CannotDeleteCustomerError', 'CannotDeleteFeatureError', 'CannotDeleteProductError', 'CannotEditPackageInNonDraftMode', 'CannotRemovePaymentMethodFromCustomerError', 'CannotReportUsageForEntitlementWithMeterError', 'CannotUpsertToPackageThatHasDraft', 'CheckoutIsNotSupported', 'CheckoutOptionsMissing', 'CouponNotFound', 'CustomerAlreadyHaveCustomerCoupon', 'CustomerAlreadyUsesCoupon', 'CustomerHasNoEmailAddress', 'CustomerHasNoPaymentMethod', 'CustomerNoBillingId', 'CustomerNotFound', 'CustomerResourceNotFound', 'DowngradeBillingPeriodNotSupportedError', 'DraftPlanCantBeArchived', 'DuplicateProductValidationError', 'DuplicatedEntityNotAllowed', 'EditAllowedOnDraftPackageOnlyError', 'EntitlementLimitExceededError', 'EntitlementsMustBelongToSamePackage', 'EntityIdDifferentFromRefIdError', 'EntityIsArchivedError', 'EnvironmentMissing', 'ExperimentAlreadyRunning', 'ExperimentNotFoundError', 'ExperimentStatusError', 'FailedToCreateCheckoutSessionError', 'FailedToImportCustomer', 'FeatureNotFound', 'FetchAllCountriesPricesNotAllowed', 'IdentityForbidden', 'ImportAlreadyInProgress', 'ImportSubscriptionsBulkError', 'InitStripePaymentMethodError', 'IntegrationNotFound', 'IntegrationValidationError', 'IntegrityViolation', 'InvalidAddressError', 'InvalidArgumentError', 'InvalidCancellationDate', 'InvalidEntitlementResetPeriod', 'InvalidMemberDelete', 'InvalidMetadataError', 'InvalidQuantity', 'InvalidSubscriptionStatus', 'InvalidUpdatePriceUnitAmountError', 'MemberInvitationError', 'MemberNotFound', 'MergeEnvironmentValidationError', 'MeterMustBeAssociatedToMeteredFeature', 'MeteringNotAvailableForFeatureType', 'MissingEntityIdError', 'NoFeatureEntitlementInSubscription', 'NoProductsAvailable', 'OperationNotAllowedDuringInProgressExperiment', 'PackageAlreadyPublished', 'PackagePricingTypeNotSet', 'PaymentMethodNotFoundError', 'PlanCannotBePublishWhenBasePlanIsDraft', 'PlanCannotBePublishWhenCompatibleAddonIsDraft', 'PlanIsUsedAsDefaultStartPlan', 'PlanIsUsedAsDowngradePlan', 'PlanNotFound', 'PlanWithChildCantBeDeleted', 'PlansCircularDependencyError', 'PriceNotFound', 'ProductNotFoundError', 'PromotionCodeCustomerNotFirstPurchase', 'PromotionCodeMaxRedemptionsReached', 'PromotionCodeMinimumAmountNotReached', 'PromotionCodeNotActive', 'PromotionCodeNotForCustomer', 'PromotionCodeNotFound', 'PromotionalEntitlementNotFoundError', 'RateLimitExceeded', 'RecalculateEntitlementsError', 'ResyncAlreadyInProgress', 'ScheduledMigrationAlreadyExistsError', 'SelectedBillingModelDoesntMatchImportedItemError', 'StripeCustomerIsDeleted', 'StripeError', 'SubscriptionAlreadyCanceledOrExpired', 'SubscriptionAlreadyOnLatestPlanError', 'SubscriptionMustHaveSinglePlanError', 'SubscriptionNotFound', 'TooManySubscriptionsPerCustomer', 'TrialMinDateError', 'TrialMustBeCancelledImmediately', 'UnPublishedPackage', 'Unauthenticated', 'UncompatibleSubscriptionAddon', 'UnexpectedError', 'UnsupportedFeatureType', 'UnsupportedSubscriptionScheduleType', 'UnsupportedVendorIdentifier')


class EventLogType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ADDON_CREATED', 'ADDON_DELETED', 'ADDON_UPDATED', 'COUPON_ARCHIVED', 'COUPON_CREATED', 'COUPON_UPDATED', 'CREATE_SUBSCRIPTION_FAILED', 'CUSTOMER_CREATED', 'CUSTOMER_DELETED', 'CUSTOMER_ENTITLEMENT_CALCULATION_TRIGGERED', 'CUSTOMER_PAYMENT_FAILED', 'CUSTOMER_RESOURCE_ENTITLEMENT_CALCULATION_TRIGGERED', 'CUSTOMER_UPDATED', 'EDGE_API_CUSTOMER_DATA_RESYNC', 'EDGE_API_DATA_RESYNC', 'EDGE_API_DOGGO_RESYNC', 'EDGE_API_PACKAGE_ENTITLEMENTS_DATA_RESYNC', 'EDGE_API_SUBSCRIPTIONS_DATA_RESYNC', 'ENTITLEMENTS_UPDATED', 'ENTITLEMENT_DENIED', 'ENTITLEMENT_GRANTED', 'ENTITLEMENT_REQUESTED', 'ENVIRONMENT_DELETED', 'FEATURE_ARCHIVED', 'FEATURE_CREATED', 'FEATURE_DELETED', 'FEATURE_UPDATED', 'IMPORT_INTEGRATION_CATALOG_TRIGGERED', 'IMPORT_INTEGRATION_CUSTOMERS_TRIGGERED', 'IMPORT_SUBSCRIPTIONS_BULK_TRIGGERED', 'MEASUREMENT_REPORTED', 'PACKAGE_PUBLISHED', 'PLAN_CREATED', 'PLAN_DELETED', 'PLAN_UPDATED', 'PRODUCT_CREATED', 'PRODUCT_DELETED', 'PRODUCT_UPDATED', 'PROMOTIONAL_ENTITLEMENT_EXPIRED', 'PROMOTIONAL_ENTITLEMENT_GRANTED', 'PROMOTIONAL_ENTITLEMENT_REVOKED', 'PROMOTIONAL_ENTITLEMENT_UPDATED', 'RECALCULATE_ENTITLEMENTS_TRIGGERED', 'RESYNC_INTEGRATION_TRIGGERED', 'SUBSCRIPTIONS_MIGRATED', 'SUBSCRIPTIONS_MIGRATION_TRIGGERED', 'SUBSCRIPTION_CANCELED', 'SUBSCRIPTION_CREATED', 'SUBSCRIPTION_EXPIRED', 'SUBSCRIPTION_TRIAL_CONVERTED', 'SUBSCRIPTION_TRIAL_ENDS_SOON', 'SUBSCRIPTION_TRIAL_EXPIRED', 'SUBSCRIPTION_TRIAL_STARTED', 'SUBSCRIPTION_UPDATED', 'SUBSCRIPTION_USAGE_UPDATED', 'SYNC_FAILED', 'WIDGET_CONFIGURATION_UPDATED')


class ExperimentSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'environmentId', 'id', 'name', 'productId', 'refId', 'status')


class ExperimentStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('COMPLETED', 'DRAFT', 'IN_PROGRESS')


class FeatureSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'description', 'displayName', 'environmentId', 'featureStatus', 'featureType', 'id', 'meterType', 'refId', 'updatedAt')


class FeatureStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ACTIVE', 'NEW', 'SUSPENDED')


class FeatureType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('BOOLEAN', 'NUMBER')


Float = sgqlc.types.Float

class FontWeight(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('BOLD', 'NORMAL')


class HookSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'endpoint', 'environmentId', 'id', 'status')


class HookStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ACTIVE', 'INACTIVE')


ID = sgqlc.types.ID

class ImportIntegrationTaskSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'environmentId', 'id', 'status', 'taskType')


Int = sgqlc.types.Int

class IntegrationSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'environmentId', 'id', 'vendorIdentifier')


class JSON(sgqlc.types.Scalar):
    __schema__ = schema


class MemberSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'id')


class MemberStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('INVITED', 'REGISTERED')


class MeterType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('Fluctuating', 'Incremental', 'None')


class MonthlyAccordingTo(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('StartOfTheMonth', 'SubscriptionStart')


class PackageDTOSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('billingId', 'createdAt', 'description', 'displayName', 'environmentId', 'id', 'isLatest', 'pricingType', 'productId', 'refId', 'status', 'updatedAt', 'versionNumber')


class PackageEntitlementSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'environmentId', 'id', 'packageId', 'updatedAt')


class PackageStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ARCHIVED', 'DRAFT', 'PUBLISHED')


class PaymentCollection(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ACTION_REQUIRED', 'FAILED', 'NOT_REQUIRED', 'PROCESSING')


class PaymentMethodType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('BANK', 'CARD')


class PlanSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('billingId', 'createdAt', 'description', 'displayName', 'environmentId', 'id', 'isLatest', 'pricingType', 'productId', 'refId', 'status', 'updatedAt', 'versionNumber')


class PriceSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('billingId', 'billingModel', 'billingPeriod', 'createdAt', 'id', 'tiersMode')


class PricingType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CUSTOM', 'FREE', 'PAID')


class ProductSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('awsMarketplaceProductCode', 'awsMarketplaceProductId', 'createdAt', 'description', 'displayName', 'environmentId', 'id', 'isDefaultProduct', 'refId', 'updatedAt')


class PromotionalEntitlementPeriod(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CUSTOM', 'LIFETIME', 'ONE_MONTH', 'ONE_WEEK', 'ONE_YEAR', 'SIX_MONTH')


class PromotionalEntitlementSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'environmentId', 'id', 'status', 'updatedAt')


class PromotionalEntitlementStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('Active', 'Expired', 'Paused')


class ProrationBehavior(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CREATE_PRORATIONS', 'INVOICE_IMMEDIATELY')


class ProvisionSubscriptionStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('PAYMENT_REQUIRED', 'SUCCESS')


class PublishMigrationType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ALL_CUSTOMERS', 'NEW_CUSTOMERS')


class SortDirection(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ASC', 'DESC')


class SortNulls(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('NULLS_FIRST', 'NULLS_LAST')


class SourceType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('JS_CLIENT_SDK', 'NODE_SERVER_SDK', 'PERSISTENT_CACHE_SERVICE')


String = sgqlc.types.String

class SubscriptionAddonSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'id', 'quantity', 'updatedAt')


class SubscriptionCancelReason(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CancelledByBilling', 'CustomerArchived', 'DetachBilling', 'Expired', 'Immediate', 'PendingPaymentExpired', 'ScheduledCancellation', 'TrialConverted', 'TrialEnded', 'UpgradeOrDowngrade')


class SubscriptionCancellationAction(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('DEFAULT', 'REVOKE_ENTITLEMENTS')


class SubscriptionCancellationTime(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('END_OF_BILLING_PERIOD', 'IMMEDIATE', 'SPECIFIC_DATE')


class SubscriptionDecisionStrategy(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('PREDEFINED_FREE_PLAN', 'PREDEFINED_TRIAL_PLAN', 'REQUESTED_PLAN', 'SKIPPED_SUBSCRIPTION_CREATION')


class SubscriptionEndSetup(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CANCEL_SUBSCRIPTION', 'DOWNGRADE_TO_FREE')


class SubscriptionEntitlementSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'environmentId', 'id', 'subscriptionId', 'updatedAt')


class SubscriptionInvoiceStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CANCELED', 'OPEN', 'PAID')


class SubscriptionMigrationTaskSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'environmentId', 'id', 'status', 'taskType')


class SubscriptionMigrationTime(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('END_OF_BILLING_PERIOD', 'IMMEDIATE')


class SubscriptionPriceSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('billingModel', 'createdAt', 'featureId', 'id', 'updatedAt', 'usageLimit')


class SubscriptionScheduleStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('Canceled', 'Done', 'Failed', 'PendingPayment', 'Scheduled')


class SubscriptionScheduleType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('Addon', 'BillingPeriod', 'Downgrade', 'MigrateToLatest', 'UnitAmount')


class SubscriptionStartSetup(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('FREE_PLAN', 'PLAN_SELECTION', 'TRIAL_PERIOD')


class SubscriptionStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ACTIVE', 'CANCELED', 'EXPIRED', 'IN_TRIAL', 'NOT_STARTED', 'PAYMENT_PENDING')


class SyncStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('ERROR', 'NO_SYNC_REQUIRED', 'PENDING', 'SUCCESS')


class TaskStatus(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CANCELED', 'COMPLETED', 'FAILED', 'IN_PROGRESS', 'PARTIALLY_FAILED', 'PENDING')


class TaskType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('IMPORT_INTEGRATION_CATALOG', 'IMPORT_INTEGRATION_CUSTOMERS', 'IMPORT_SUBSCRIPTIONS_BULK', 'RECALCULATE_BATCH_ENTITLEMENTS', 'RECALCULATE_ENTITLEMENTS', 'RESYNC_INTEGRATION', 'SUBSCRIPTION_MIGRATION', 'SUBSCRIPTION_MIGRATION_V2')


class TiersMode(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('GRADUATED', 'VOLUME')


class TrialPeriodUnits(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('DAY', 'MONTH')


class UsageMeasurementSortFields(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('createdAt', 'environmentId', 'id')


class UsageUpdateBehavior(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('DELTA', 'SET')


class VendorIdentifier(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('AWS_MARKETPLACE', 'HUBSPOT', 'STRIPE', 'ZUORA')


class WeeklyAccordingTo(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('EveryFriday', 'EveryMonday', 'EverySaturday', 'EverySunday', 'EveryThursday', 'EveryTuesday', 'EveryWednesday', 'SubscriptionStart')


class WidgetType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CHECKOUT', 'CUSTOMER_PORTAL', 'PAYWALL')


class YearlyAccordingTo(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('SubscriptionStart',)


class experimentGroupType(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ('CONTROL', 'VARIANT')



########################################################################
# Input Objects
########################################################################
class AddCompatibleAddonsToPlanInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_ids')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='relationIds')


class AddonCreateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'aws_marketplace_plan_dimension', 'billing_id', 'description', 'display_name', 'environment_id', 'hidden_from_widgets', 'pricing_type', 'product_id', 'ref_id', 'status')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    aws_marketplace_plan_dimension = sgqlc.types.Field(String, graphql_name='awsMarketplacePlanDimension')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')


class AddonFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'or_', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('AddonFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    is_latest = sgqlc.types.Field('BooleanFieldComparison', graphql_name='isLatest')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('AddonFilter')), graphql_name='or')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='productId')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    status = sgqlc.types.Field('PackageStatusFilterComparison', graphql_name='status')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')
    version_number = sgqlc.types.Field('IntFieldComparison', graphql_name='versionNumber')


class AddonSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(AddonSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class AddonUpdateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'billing_id', 'description', 'display_name', 'hidden_from_widgets', 'id', 'status')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')


class Address(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('address_line1', 'address_line2', 'city', 'country', 'phone_number', 'postal_code', 'state')
    address_line1 = sgqlc.types.Field(String, graphql_name='addressLine1')
    address_line2 = sgqlc.types.Field(String, graphql_name='addressLine2')
    city = sgqlc.types.Field(String, graphql_name='city')
    country = sgqlc.types.Field(String, graphql_name='country')
    phone_number = sgqlc.types.Field(String, graphql_name='phoneNumber')
    postal_code = sgqlc.types.Field(String, graphql_name='postalCode')
    state = sgqlc.types.Field(String, graphql_name='state')


class AggregatedEventsByCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('aggregation', 'customer_id', 'environment_id', 'filters')
    aggregation = sgqlc.types.Field(sgqlc.types.non_null('MeterAggregation'), graphql_name='aggregation')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    filters = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MeterFilterDefinitionInput'))), graphql_name='filters')


class ApiKeyFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'id', 'or_')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ApiKeyFilter')), graphql_name='and')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ApiKeyFilter')), graphql_name='or')


class ApiKeySort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(ApiKeySortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class ApplySubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'addons', 'billable_features', 'billing_country_code', 'billing_id', 'billing_information', 'billing_period', 'customer_id', 'payment_method_id', 'plan_id', 'promotion_code', 'resource_id', 'skip_trial', 'start_date', 'subscription_entitlements', 'trial_override_configuration', 'unit_quantity')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonInput')), graphql_name='addons')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('BillableFeatureInput')), graphql_name='billableFeatures')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_information = sgqlc.types.Field('SubscriptionBillingInfo', graphql_name='billingInformation')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    payment_method_id = sgqlc.types.Field(String, graphql_name='paymentMethodId')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')
    promotion_code = sgqlc.types.Field(String, graphql_name='promotionCode')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    skip_trial = sgqlc.types.Field(Boolean, graphql_name='skipTrial')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    subscription_entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementInput')), graphql_name='subscriptionEntitlements')
    trial_override_configuration = sgqlc.types.Field('TrialOverrideConfigurationInput', graphql_name='trialOverrideConfiguration')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class ArchiveCouponInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'ref_id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class ArchiveCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')


class ArchiveEnvironmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'slug')
    id = sgqlc.types.Field(String, graphql_name='id')
    slug = sgqlc.types.Field(String, graphql_name='slug')


class ArchiveFeatureInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class ArchivePlanInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class AttachCustomerPaymentMethodInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id', 'payment_method_id', 'ref_id', 'vendor_identifier')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    payment_method_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='paymentMethodId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    vendor_identifier = sgqlc.types.Field(sgqlc.types.non_null(VendorIdentifier), graphql_name='vendorIdentifier')


class AwsMarketplaceCredentialsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('aws_role_arn',)
    aws_role_arn = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='awsRoleArn')


class BillableFeatureInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('feature_id', 'quantity')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    quantity = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='quantity')


class BillingAddress(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('city', 'country', 'line1', 'line2', 'postal_code', 'state')
    city = sgqlc.types.Field(String, graphql_name='city')
    country = sgqlc.types.Field(String, graphql_name='country')
    line1 = sgqlc.types.Field(String, graphql_name='line1')
    line2 = sgqlc.types.Field(String, graphql_name='line2')
    postal_code = sgqlc.types.Field(String, graphql_name='postalCode')
    state = sgqlc.types.Field(String, graphql_name='state')


class BillingModelFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(BillingModel, graphql_name='eq')
    gt = sgqlc.types.Field(BillingModel, graphql_name='gt')
    gte = sgqlc.types.Field(BillingModel, graphql_name='gte')
    i_like = sgqlc.types.Field(BillingModel, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillingModel)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(BillingModel, graphql_name='like')
    lt = sgqlc.types.Field(BillingModel, graphql_name='lt')
    lte = sgqlc.types.Field(BillingModel, graphql_name='lte')
    neq = sgqlc.types.Field(BillingModel, graphql_name='neq')
    not_ilike = sgqlc.types.Field(BillingModel, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillingModel)), graphql_name='notIn')
    not_like = sgqlc.types.Field(BillingModel, graphql_name='notLike')


class BillingPeriodFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(BillingPeriod, graphql_name='eq')
    gt = sgqlc.types.Field(BillingPeriod, graphql_name='gt')
    gte = sgqlc.types.Field(BillingPeriod, graphql_name='gte')
    i_like = sgqlc.types.Field(BillingPeriod, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillingPeriod)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(BillingPeriod, graphql_name='like')
    lt = sgqlc.types.Field(BillingPeriod, graphql_name='lt')
    lte = sgqlc.types.Field(BillingPeriod, graphql_name='lte')
    neq = sgqlc.types.Field(BillingPeriod, graphql_name='neq')
    not_ilike = sgqlc.types.Field(BillingPeriod, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillingPeriod)), graphql_name='notIn')
    not_like = sgqlc.types.Field(BillingPeriod, graphql_name='notLike')


class BooleanFieldComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('is_', 'is_not')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')


class CheckoutConfigurationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('content', 'custom_css', 'palette', 'typography')
    content = sgqlc.types.Field('CheckoutContentInput', graphql_name='content')
    custom_css = sgqlc.types.Field(String, graphql_name='customCss')
    palette = sgqlc.types.Field('CheckoutPaletteInput', graphql_name='palette')
    typography = sgqlc.types.Field('TypographyConfigurationInput', graphql_name='typography')


class CheckoutContentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('collect_phone_number',)
    collect_phone_number = sgqlc.types.Field(Boolean, graphql_name='collectPhoneNumber')


class CheckoutOptions(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('allow_promo_codes', 'allow_tax_id_collection', 'cancel_url', 'collect_billing_address', 'collect_phone_number', 'reference_id', 'success_url')
    allow_promo_codes = sgqlc.types.Field(Boolean, graphql_name='allowPromoCodes')
    allow_tax_id_collection = sgqlc.types.Field(Boolean, graphql_name='allowTaxIdCollection')
    cancel_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='cancelUrl')
    collect_billing_address = sgqlc.types.Field(Boolean, graphql_name='collectBillingAddress')
    collect_phone_number = sgqlc.types.Field(Boolean, graphql_name='collectPhoneNumber')
    reference_id = sgqlc.types.Field(String, graphql_name='referenceId')
    success_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='successUrl')


class CheckoutPaletteInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('background_color', 'border_color', 'primary', 'summary_background_color', 'text_color')
    background_color = sgqlc.types.Field(String, graphql_name='backgroundColor')
    border_color = sgqlc.types.Field(String, graphql_name='borderColor')
    primary = sgqlc.types.Field(String, graphql_name='primary')
    summary_background_color = sgqlc.types.Field(String, graphql_name='summaryBackgroundColor')
    text_color = sgqlc.types.Field(String, graphql_name='textColor')


class CheckoutStateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('billing_country_code', 'customer_id', 'plan_id', 'resource_id')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class ClearCustomerPersistentCacheInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id', 'resource_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class CouponFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'customers', 'description', 'environment_id', 'id', 'name', 'or_', 'ref_id', 'status', 'type', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CouponFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    customers = sgqlc.types.Field('CouponFilterCustomerFilter', graphql_name='customers')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    name = sgqlc.types.Field('StringFieldComparison', graphql_name='name')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CouponFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    status = sgqlc.types.Field('CouponStatusFilterComparison', graphql_name='status')
    type = sgqlc.types.Field('CouponTypeFilterComparison', graphql_name='type')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')


class CouponFilterCustomerFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'or_', 'ref_id', 'search_query', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CouponFilterCustomerFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmId')
    customer_id = sgqlc.types.Field('StringFieldComparison', graphql_name='customerId')
    deleted_at = sgqlc.types.Field('DateFieldComparison', graphql_name='deletedAt')
    email = sgqlc.types.Field('StringFieldComparison', graphql_name='email')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    name = sgqlc.types.Field('StringFieldComparison', graphql_name='name')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CouponFilterCustomerFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    search_query = sgqlc.types.Field('CustomerSearchQueryFilterComparison', graphql_name='searchQuery')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')


class CouponSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(CouponSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class CouponStatusFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(CouponStatus, graphql_name='eq')
    gt = sgqlc.types.Field(CouponStatus, graphql_name='gt')
    gte = sgqlc.types.Field(CouponStatus, graphql_name='gte')
    i_like = sgqlc.types.Field(CouponStatus, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CouponStatus)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(CouponStatus, graphql_name='like')
    lt = sgqlc.types.Field(CouponStatus, graphql_name='lt')
    lte = sgqlc.types.Field(CouponStatus, graphql_name='lte')
    neq = sgqlc.types.Field(CouponStatus, graphql_name='neq')
    not_ilike = sgqlc.types.Field(CouponStatus, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CouponStatus)), graphql_name='notIn')
    not_like = sgqlc.types.Field(CouponStatus, graphql_name='notLike')


class CouponTypeFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(CouponType, graphql_name='eq')
    gt = sgqlc.types.Field(CouponType, graphql_name='gt')
    gte = sgqlc.types.Field(CouponType, graphql_name='gte')
    i_like = sgqlc.types.Field(CouponType, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CouponType)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(CouponType, graphql_name='like')
    lt = sgqlc.types.Field(CouponType, graphql_name='lt')
    lte = sgqlc.types.Field(CouponType, graphql_name='lte')
    neq = sgqlc.types.Field(CouponType, graphql_name='neq')
    not_ilike = sgqlc.types.Field(CouponType, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CouponType)), graphql_name='notIn')
    not_like = sgqlc.types.Field(CouponType, graphql_name='notLike')


class CreateCouponInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'description', 'discount_value', 'environment_id', 'name', 'ref_id', 'type')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    description = sgqlc.types.Field(String, graphql_name='description')
    discount_value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='discountValue')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    type = sgqlc.types.Field(sgqlc.types.non_null(CouponType), graphql_name='type')


class CreateEnvironment(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('color', 'created_at', 'description', 'display_name', 'harden_client_access_enabled', 'id', 'provision_status', 'slug', 'type')
    color = sgqlc.types.Field(String, graphql_name='color')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    harden_client_access_enabled = sgqlc.types.Field(Boolean, graphql_name='hardenClientAccessEnabled')
    id = sgqlc.types.Field(String, graphql_name='id')
    provision_status = sgqlc.types.Field(EnvironmentProvisionStatus, graphql_name='provisionStatus')
    slug = sgqlc.types.Field(String, graphql_name='slug')
    type = sgqlc.types.Field(EnvironmentType, graphql_name='type')


class CreateEnvironmentOptions(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('create_default_product',)
    create_default_product = sgqlc.types.Field(Boolean, graphql_name='createDefaultProduct')


class CreateExperimentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('control_group_name', 'description', 'environment_id', 'name', 'product_id', 'product_settings', 'variant_group_name', 'variant_percentage')
    control_group_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='controlGroupName')
    description = sgqlc.types.Field(String, graphql_name='description')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productId')
    product_settings = sgqlc.types.Field('ProductSettingsInput', graphql_name='productSettings')
    variant_group_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='variantGroupName')
    variant_percentage = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='variantPercentage')


class CreateHook(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'endpoint', 'environment_id', 'event_log_types', 'id', 'secret_key', 'status')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    endpoint = sgqlc.types.Field(String, graphql_name='endpoint')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    event_log_types = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(EventLogType)), graphql_name='eventLogTypes')
    id = sgqlc.types.Field(String, graphql_name='id')
    secret_key = sgqlc.types.Field(String, graphql_name='secretKey')
    status = sgqlc.types.Field(HookStatus, graphql_name='status')


class CreateIntegrationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('aws_marketplace_credentials', 'environment_id', 'hubspot_credentials', 'stripe_credentials', 'vendor_identifier', 'zuora_credentials')
    aws_marketplace_credentials = sgqlc.types.Field(AwsMarketplaceCredentialsInput, graphql_name='awsMarketplaceCredentials')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    hubspot_credentials = sgqlc.types.Field('HubspotCredentialsInput', graphql_name='hubspotCredentials')
    stripe_credentials = sgqlc.types.Field('StripeCredentialsInput', graphql_name='stripeCredentials')
    vendor_identifier = sgqlc.types.Field(sgqlc.types.non_null(VendorIdentifier), graphql_name='vendorIdentifier')
    zuora_credentials = sgqlc.types.Field('ZuoraCredentialsInput', graphql_name='zuoraCredentials')


class CreateManyPackageEntitlementsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('package_entitlements',)
    package_entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlementInput'))), graphql_name='packageEntitlements')


class CreateManyPromotionalEntitlementsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('promotional_entitlements',)
    promotional_entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PromotionalEntitlementInput'))), graphql_name='promotionalEntitlements')


class CreateMeter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('aggregation', 'filters')
    aggregation = sgqlc.types.Field(sgqlc.types.non_null('MeterAggregation'), graphql_name='aggregation')
    filters = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MeterFilterDefinitionInput'))), graphql_name='filters')


class CreateOneEnvironmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment', 'options')
    environment = sgqlc.types.Field(sgqlc.types.non_null(CreateEnvironment), graphql_name='environment')
    options = sgqlc.types.Field(CreateEnvironmentOptions, graphql_name='options')


class CreateOneFeatureInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('feature',)
    feature = sgqlc.types.Field(sgqlc.types.non_null('FeatureInput'), graphql_name='feature')


class CreateOneHookInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('hook',)
    hook = sgqlc.types.Field(sgqlc.types.non_null(CreateHook), graphql_name='hook')


class CreateOneIntegrationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('integration',)
    integration = sgqlc.types.Field(sgqlc.types.non_null(CreateIntegrationInput), graphql_name='integration')


class CreateOneProductInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('product',)
    product = sgqlc.types.Field(sgqlc.types.non_null('ProductCreateInput'), graphql_name='product')


class CreateOrUpdateAwsMarketplaceProductInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'aws_dimensions_mapping', 'aws_product_id', 'description', 'display_name', 'environment_id', 'multiple_subscriptions', 'product_id', 'product_settings', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    aws_dimensions_mapping = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('DimensionsMappingInput'))), graphql_name='awsDimensionsMapping')
    aws_product_id = sgqlc.types.Field(String, graphql_name='awsProductId')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    multiple_subscriptions = sgqlc.types.Field(Boolean, graphql_name='multipleSubscriptions')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    product_settings = sgqlc.types.Field('ProductSettingsInput', graphql_name='productSettings')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')


class CursorPaging(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'first', 'last')
    after = sgqlc.types.Field(ConnectionCursor, graphql_name='after')
    before = sgqlc.types.Field(ConnectionCursor, graphql_name='before')
    first = sgqlc.types.Field(Int, graphql_name='first')
    last = sgqlc.types.Field(Int, graphql_name='last')


class CustomerBillingInfo(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('billing_address', 'currency', 'customer_name', 'invoice_custom_fields', 'language', 'metadata', 'payment_method_id', 'shipping_address', 'tax_ids', 'timezone')
    billing_address = sgqlc.types.Field(Address, graphql_name='billingAddress')
    currency = sgqlc.types.Field(Currency, graphql_name='currency')
    customer_name = sgqlc.types.Field(String, graphql_name='customerName')
    invoice_custom_fields = sgqlc.types.Field(JSON, graphql_name='invoiceCustomFields')
    language = sgqlc.types.Field(String, graphql_name='language')
    metadata = sgqlc.types.Field(JSON, graphql_name='metadata')
    payment_method_id = sgqlc.types.Field(String, graphql_name='paymentMethodId')
    shipping_address = sgqlc.types.Field(Address, graphql_name='shippingAddress')
    tax_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('TaxExempt')), graphql_name='taxIds')
    timezone = sgqlc.types.Field(String, graphql_name='timezone')


class CustomerFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'or_', 'promotional_entitlements', 'ref_id', 'search_query', 'subscriptions', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmId')
    customer_id = sgqlc.types.Field('StringFieldComparison', graphql_name='customerId')
    deleted_at = sgqlc.types.Field('DateFieldComparison', graphql_name='deletedAt')
    email = sgqlc.types.Field('StringFieldComparison', graphql_name='email')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    name = sgqlc.types.Field('StringFieldComparison', graphql_name='name')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerFilter')), graphql_name='or')
    promotional_entitlements = sgqlc.types.Field('CustomerFilterPromotionalEntitlementFilter', graphql_name='promotionalEntitlements')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    search_query = sgqlc.types.Field('CustomerSearchQueryFilterComparison', graphql_name='searchQuery')
    subscriptions = sgqlc.types.Field('CustomerFilterCustomerSubscriptionFilter', graphql_name='subscriptions')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')


class CustomerFilterCustomerSubscriptionFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'or_', 'payment_collection', 'pricing_type', 'ref_id', 'resource_id', 'start_date', 'status', 'subscription_id', 'trial_end_date')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerFilterCustomerSubscriptionFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    cancel_reason = sgqlc.types.Field('SubscriptionCancelReasonFilterComparison', graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field('DateFieldComparison', graphql_name='cancellationDate')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    crm_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmId')
    crm_link_url = sgqlc.types.Field('StringFieldComparison', graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field('DateFieldComparison', graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field('DateFieldComparison', graphql_name='currentBillingPeriodStart')
    effective_end_date = sgqlc.types.Field('DateFieldComparison', graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field('DateFieldComparison', graphql_name='endDate')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    old_billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='oldBillingId')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerFilterCustomerSubscriptionFilter')), graphql_name='or')
    payment_collection = sgqlc.types.Field('PaymentCollectionFilterComparison', graphql_name='paymentCollection')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    resource_id = sgqlc.types.Field('StringFieldComparison', graphql_name='resourceId')
    start_date = sgqlc.types.Field('DateFieldComparison', graphql_name='startDate')
    status = sgqlc.types.Field('SubscriptionStatusFilterComparison', graphql_name='status')
    subscription_id = sgqlc.types.Field('StringFieldComparison', graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field('DateFieldComparison', graphql_name='trialEndDate')


class CustomerFilterPromotionalEntitlementFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'environment_id', 'id', 'or_', 'status', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerFilterPromotionalEntitlementFilter')), graphql_name='and')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerFilterPromotionalEntitlementFilter')), graphql_name='or')
    status = sgqlc.types.Field('PromotionalEntitlementStatusFilterComparison', graphql_name='status')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')


class CustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'aws_marketplace_customer_id', 'billing_id', 'billing_information', 'coupon_ref_id', 'created_at', 'crm_id', 'customer_id', 'email', 'environment_id', 'name', 'ref_id', 'should_sync_free')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    aws_marketplace_customer_id = sgqlc.types.Field(String, graphql_name='awsMarketplaceCustomerId')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_information = sgqlc.types.Field(CustomerBillingInfo, graphql_name='billingInformation')
    coupon_ref_id = sgqlc.types.Field(String, graphql_name='couponRefId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    email = sgqlc.types.Field(String, graphql_name='email')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    name = sgqlc.types.Field(String, graphql_name='name')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    should_sync_free = sgqlc.types.Field(Boolean, graphql_name='shouldSyncFree')


class CustomerPortalColorsPaletteInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('background_color', 'border_color', 'current_plan_background', 'icons_color', 'paywall_background_color', 'primary', 'text_color')
    background_color = sgqlc.types.Field(String, graphql_name='backgroundColor')
    border_color = sgqlc.types.Field(String, graphql_name='borderColor')
    current_plan_background = sgqlc.types.Field(String, graphql_name='currentPlanBackground')
    icons_color = sgqlc.types.Field(String, graphql_name='iconsColor')
    paywall_background_color = sgqlc.types.Field(String, graphql_name='paywallBackgroundColor')
    primary = sgqlc.types.Field(String, graphql_name='primary')
    text_color = sgqlc.types.Field(String, graphql_name='textColor')


class CustomerPortalConfigurationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('custom_css', 'palette', 'typography')
    custom_css = sgqlc.types.Field(String, graphql_name='customCss')
    palette = sgqlc.types.Field(CustomerPortalColorsPaletteInput, graphql_name='palette')
    typography = sgqlc.types.Field('TypographyConfigurationInput', graphql_name='typography')


class CustomerPortalInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'product_id', 'resource_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class CustomerResourceFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'customer', 'environment_id', 'or_', 'resource_id', 'subscriptions')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerResourceFilter')), graphql_name='and')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    customer = sgqlc.types.Field('CustomerResourceFilterCustomerFilter', graphql_name='customer')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerResourceFilter')), graphql_name='or')
    resource_id = sgqlc.types.Field('StringFieldComparison', graphql_name='resourceId')
    subscriptions = sgqlc.types.Field('CustomerResourceFilterCustomerSubscriptionFilter', graphql_name='subscriptions')


class CustomerResourceFilterCustomerFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'or_', 'ref_id', 'search_query', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerResourceFilterCustomerFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmId')
    customer_id = sgqlc.types.Field('StringFieldComparison', graphql_name='customerId')
    deleted_at = sgqlc.types.Field('DateFieldComparison', graphql_name='deletedAt')
    email = sgqlc.types.Field('StringFieldComparison', graphql_name='email')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    name = sgqlc.types.Field('StringFieldComparison', graphql_name='name')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerResourceFilterCustomerFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    search_query = sgqlc.types.Field('CustomerSearchQueryFilterComparison', graphql_name='searchQuery')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')


class CustomerResourceFilterCustomerSubscriptionFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'or_', 'payment_collection', 'pricing_type', 'ref_id', 'resource_id', 'start_date', 'status', 'subscription_id', 'trial_end_date')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerResourceFilterCustomerSubscriptionFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    cancel_reason = sgqlc.types.Field('SubscriptionCancelReasonFilterComparison', graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field('DateFieldComparison', graphql_name='cancellationDate')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    crm_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmId')
    crm_link_url = sgqlc.types.Field('StringFieldComparison', graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field('DateFieldComparison', graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field('DateFieldComparison', graphql_name='currentBillingPeriodStart')
    effective_end_date = sgqlc.types.Field('DateFieldComparison', graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field('DateFieldComparison', graphql_name='endDate')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    old_billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='oldBillingId')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerResourceFilterCustomerSubscriptionFilter')), graphql_name='or')
    payment_collection = sgqlc.types.Field('PaymentCollectionFilterComparison', graphql_name='paymentCollection')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    resource_id = sgqlc.types.Field('StringFieldComparison', graphql_name='resourceId')
    start_date = sgqlc.types.Field('DateFieldComparison', graphql_name='startDate')
    status = sgqlc.types.Field('SubscriptionStatusFilterComparison', graphql_name='status')
    subscription_id = sgqlc.types.Field('StringFieldComparison', graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field('DateFieldComparison', graphql_name='trialEndDate')


class CustomerResourceSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(CustomerResourceSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class CustomerSearchQueryFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('i_like',)
    i_like = sgqlc.types.Field(String, graphql_name='iLike')


class CustomerSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(CustomerSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class CustomerSubscriptionFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('addons', 'and_', 'billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'customer', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'or_', 'payment_collection', 'plan', 'prices', 'pricing_type', 'ref_id', 'resource', 'resource_id', 'start_date', 'status', 'subscription_entitlements', 'subscription_id', 'trial_end_date')
    addons = sgqlc.types.Field('CustomerSubscriptionFilterSubscriptionAddonFilter', graphql_name='addons')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    cancel_reason = sgqlc.types.Field('SubscriptionCancelReasonFilterComparison', graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field('DateFieldComparison', graphql_name='cancellationDate')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    crm_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmId')
    crm_link_url = sgqlc.types.Field('StringFieldComparison', graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field('DateFieldComparison', graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field('DateFieldComparison', graphql_name='currentBillingPeriodStart')
    customer = sgqlc.types.Field('CustomerSubscriptionFilterCustomerFilter', graphql_name='customer')
    effective_end_date = sgqlc.types.Field('DateFieldComparison', graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field('DateFieldComparison', graphql_name='endDate')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    old_billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='oldBillingId')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilter')), graphql_name='or')
    payment_collection = sgqlc.types.Field('PaymentCollectionFilterComparison', graphql_name='paymentCollection')
    plan = sgqlc.types.Field('CustomerSubscriptionFilterPlanFilter', graphql_name='plan')
    prices = sgqlc.types.Field('CustomerSubscriptionFilterSubscriptionPriceFilter', graphql_name='prices')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    resource = sgqlc.types.Field('CustomerSubscriptionFilterCustomerResourceFilter', graphql_name='resource')
    resource_id = sgqlc.types.Field('StringFieldComparison', graphql_name='resourceId')
    start_date = sgqlc.types.Field('DateFieldComparison', graphql_name='startDate')
    status = sgqlc.types.Field('SubscriptionStatusFilterComparison', graphql_name='status')
    subscription_entitlements = sgqlc.types.Field('CustomerSubscriptionFilterSubscriptionEntitlementFilter', graphql_name='subscriptionEntitlements')
    subscription_id = sgqlc.types.Field('StringFieldComparison', graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field('DateFieldComparison', graphql_name='trialEndDate')


class CustomerSubscriptionFilterCustomerFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'or_', 'ref_id', 'search_query', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterCustomerFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmId')
    customer_id = sgqlc.types.Field('StringFieldComparison', graphql_name='customerId')
    deleted_at = sgqlc.types.Field('DateFieldComparison', graphql_name='deletedAt')
    email = sgqlc.types.Field('StringFieldComparison', graphql_name='email')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    name = sgqlc.types.Field('StringFieldComparison', graphql_name='name')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterCustomerFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    search_query = sgqlc.types.Field(CustomerSearchQueryFilterComparison, graphql_name='searchQuery')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')


class CustomerSubscriptionFilterCustomerResourceFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'environment_id', 'or_', 'resource_id')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterCustomerResourceFilter')), graphql_name='and')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterCustomerResourceFilter')), graphql_name='or')
    resource_id = sgqlc.types.Field('StringFieldComparison', graphql_name='resourceId')


class CustomerSubscriptionFilterPlanFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'or_', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterPlanFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    is_latest = sgqlc.types.Field(BooleanFieldComparison, graphql_name='isLatest')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterPlanFilter')), graphql_name='or')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='productId')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    status = sgqlc.types.Field('PackageStatusFilterComparison', graphql_name='status')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')
    version_number = sgqlc.types.Field('IntFieldComparison', graphql_name='versionNumber')


class CustomerSubscriptionFilterSubscriptionAddonFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'id', 'or_', 'quantity', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterSubscriptionAddonFilter')), graphql_name='and')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterSubscriptionAddonFilter')), graphql_name='or')
    quantity = sgqlc.types.Field('NumberFieldComparison', graphql_name='quantity')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')


class CustomerSubscriptionFilterSubscriptionEntitlementFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'environment_id', 'id', 'or_', 'subscription_id', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterSubscriptionEntitlementFilter')), graphql_name='and')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterSubscriptionEntitlementFilter')), graphql_name='or')
    subscription_id = sgqlc.types.Field('StringFieldComparison', graphql_name='subscriptionId')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')


class CustomerSubscriptionFilterSubscriptionPriceFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_model', 'created_at', 'feature_id', 'id', 'or_', 'updated_at', 'usage_limit')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterSubscriptionPriceFilter')), graphql_name='and')
    billing_model = sgqlc.types.Field(BillingModelFilterComparison, graphql_name='billingModel')
    created_at = sgqlc.types.Field('DateFieldComparison', graphql_name='createdAt')
    feature_id = sgqlc.types.Field('StringFieldComparison', graphql_name='featureId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionFilterSubscriptionPriceFilter')), graphql_name='or')
    updated_at = sgqlc.types.Field('DateFieldComparison', graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field('NumberFieldComparison', graphql_name='usageLimit')


class CustomerSubscriptionSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscriptionSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class DateFieldComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('between', 'eq', 'gt', 'gte', 'in_', 'is_', 'is_not', 'lt', 'lte', 'neq', 'not_between', 'not_in')
    between = sgqlc.types.Field('DateFieldComparisonBetween', graphql_name='between')
    eq = sgqlc.types.Field(DateTime, graphql_name='eq')
    gt = sgqlc.types.Field(DateTime, graphql_name='gt')
    gte = sgqlc.types.Field(DateTime, graphql_name='gte')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DateTime)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    lt = sgqlc.types.Field(DateTime, graphql_name='lt')
    lte = sgqlc.types.Field(DateTime, graphql_name='lte')
    neq = sgqlc.types.Field(DateTime, graphql_name='neq')
    not_between = sgqlc.types.Field('DateFieldComparisonBetween', graphql_name='notBetween')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(DateTime)), graphql_name='notIn')


class DateFieldComparisonBetween(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('lower', 'upper')
    lower = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='lower')
    upper = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='upper')


class DefaultTrialConfigInputDTO(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('duration', 'units')
    duration = sgqlc.types.Field(Float, graphql_name='duration')
    units = sgqlc.types.Field(TrialPeriodUnits, graphql_name='units')


class DeleteFeatureInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class DeleteOneAddonInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class DeleteOneHookInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class DeleteOneIntegrationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class DeleteOnePackageEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class DeleteOnePriceInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class DeleteOneProductInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class DeleteOnePromotionalEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class DetachCustomerPaymentMethodInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')


class DimensionsMappingInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('key', 'plan_name', 'plan_ref_id')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    plan_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planName')
    plan_ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planRefId')


class DiscardPackageDraftInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'ref_id')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class DoesFeatureExist(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'ref_id')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class DumpEnvironmentForForMergeComparisonInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('destination_environment_slug', 'source_environment_slug')
    destination_environment_slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='destinationEnvironmentSlug')
    source_environment_slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourceEnvironmentSlug')


class DumpEnvironmentProductCatalogInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_slug',)
    environment_slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentSlug')


class DuplicateProductInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('description', 'display_name', 'environment_id', 'ref_id', 'source_product_id')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    source_product_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourceProductId')


class EntitlementCheckRequested(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'entitlement_check_result', 'environment_id', 'feature_id', 'requested_usage', 'resource_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    entitlement_check_result = sgqlc.types.Field(sgqlc.types.non_null('EntitlementCheckResult'), graphql_name='entitlementCheckResult')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    requested_usage = sgqlc.types.Field(Float, graphql_name='requestedUsage')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class EntitlementCheckResult(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('access_denied_reason', 'current_usage', 'has_access', 'has_unlimited_usage', 'monthly_reset_period_configuration', 'next_reset_date', 'requested_usage', 'reset_period', 'usage_limit', 'weekly_reset_period_configuration', 'yearly_reset_period_configuration')
    access_denied_reason = sgqlc.types.Field(AccessDeniedReason, graphql_name='accessDeniedReason')
    current_usage = sgqlc.types.Field(Float, graphql_name='currentUsage')
    has_access = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasAccess')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    monthly_reset_period_configuration = sgqlc.types.Field('MonthlyResetPeriodConfigInput', graphql_name='monthlyResetPeriodConfiguration')
    next_reset_date = sgqlc.types.Field(DateTime, graphql_name='nextResetDate')
    requested_usage = sgqlc.types.Field(Float, graphql_name='requestedUsage')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')
    yearly_reset_period_configuration = sgqlc.types.Field('YearlyResetPeriodConfigInput', graphql_name='yearlyResetPeriodConfiguration')


class EntitlementOptions(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('requested_usage', 'should_track')
    requested_usage = sgqlc.types.Field(Float, graphql_name='requestedUsage')
    should_track = sgqlc.types.Field(Boolean, graphql_name='shouldTrack')


class EnvironmentFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'display_name', 'id', 'or_', 'permanent_deletion_date', 'slug')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('EnvironmentFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('EnvironmentFilter')), graphql_name='or')
    permanent_deletion_date = sgqlc.types.Field(DateFieldComparison, graphql_name='permanentDeletionDate')
    slug = sgqlc.types.Field('StringFieldComparison', graphql_name='slug')


class EnvironmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('color', 'description', 'display_name', 'harden_client_access_enabled', 'provision_status')
    color = sgqlc.types.Field(String, graphql_name='color')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    harden_client_access_enabled = sgqlc.types.Field(Boolean, graphql_name='hardenClientAccessEnabled')
    provision_status = sgqlc.types.Field(EnvironmentProvisionStatus, graphql_name='provisionStatus')


class EnvironmentSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(EnvironmentSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class EstimateSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('addons', 'billable_features', 'billing_country_code', 'billing_information', 'billing_period', 'customer_id', 'environment_id', 'plan_id', 'price_unit_amount', 'promotion_code', 'resource_id', 'skip_trial', 'start_date', 'unit_quantity')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonInput')), graphql_name='addons')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillableFeatureInput)), graphql_name='billableFeatures')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_information = sgqlc.types.Field('SubscriptionBillingInfo', graphql_name='billingInformation')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')
    price_unit_amount = sgqlc.types.Field(Float, graphql_name='priceUnitAmount')
    promotion_code = sgqlc.types.Field(String, graphql_name='promotionCode')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    skip_trial = sgqlc.types.Field(Boolean, graphql_name='skipTrial')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class EstimateSubscriptionUpdateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('addons', 'billable_features', 'environment_id', 'promotion_code', 'subscription_id', 'unit_quantity')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonInput')), graphql_name='addons')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillableFeatureInput)), graphql_name='billableFeatures')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    promotion_code = sgqlc.types.Field(String, graphql_name='promotionCode')
    subscription_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subscriptionId')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class EventsFieldsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'filters')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    filters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('MeterFilterDefinitionInput')), graphql_name='filters')


class ExperimentFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'customers', 'environment_id', 'id', 'name', 'or_', 'product_id', 'ref_id', 'status')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ExperimentFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    customers = sgqlc.types.Field('ExperimentFilterCustomerFilter', graphql_name='customers')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    name = sgqlc.types.Field('StringFieldComparison', graphql_name='name')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ExperimentFilter')), graphql_name='or')
    product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='productId')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    status = sgqlc.types.Field('ExperimentStatusFilterComparison', graphql_name='status')


class ExperimentFilterCustomerFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'or_', 'ref_id', 'search_query', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ExperimentFilterCustomerFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field('StringFieldComparison', graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field('StringFieldComparison', graphql_name='crmId')
    customer_id = sgqlc.types.Field('StringFieldComparison', graphql_name='customerId')
    deleted_at = sgqlc.types.Field(DateFieldComparison, graphql_name='deletedAt')
    email = sgqlc.types.Field('StringFieldComparison', graphql_name='email')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    name = sgqlc.types.Field('StringFieldComparison', graphql_name='name')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ExperimentFilterCustomerFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    search_query = sgqlc.types.Field(CustomerSearchQueryFilterComparison, graphql_name='searchQuery')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class ExperimentSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(ExperimentSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class ExperimentStatsQuery(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'experiment_ref_id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    experiment_ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='experimentRefId')


class ExperimentStatusFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(ExperimentStatus, graphql_name='eq')
    gt = sgqlc.types.Field(ExperimentStatus, graphql_name='gt')
    gte = sgqlc.types.Field(ExperimentStatus, graphql_name='gte')
    i_like = sgqlc.types.Field(ExperimentStatus, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ExperimentStatus)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(ExperimentStatus, graphql_name='like')
    lt = sgqlc.types.Field(ExperimentStatus, graphql_name='lt')
    lte = sgqlc.types.Field(ExperimentStatus, graphql_name='lte')
    neq = sgqlc.types.Field(ExperimentStatus, graphql_name='neq')
    not_ilike = sgqlc.types.Field(ExperimentStatus, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ExperimentStatus)), graphql_name='notIn')
    not_like = sgqlc.types.Field(ExperimentStatus, graphql_name='notLike')


class FeatureAssociatedLatestPackages(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'feature_id')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')


class FeatureFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'id', 'meter_type', 'or_', 'ref_id', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('FeatureFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    feature_status = sgqlc.types.Field('FeatureStatusFilterComparison', graphql_name='featureStatus')
    feature_type = sgqlc.types.Field('FeatureTypeFilterComparison', graphql_name='featureType')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    meter_type = sgqlc.types.Field('MeterTypeFilterComparison', graphql_name='meterType')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('FeatureFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class FeatureInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'feature_units', 'feature_units_plural', 'meter', 'meter_type', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature_status = sgqlc.types.Field(FeatureStatus, graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(sgqlc.types.non_null(FeatureType), graphql_name='featureType')
    feature_units = sgqlc.types.Field(String, graphql_name='featureUnits')
    feature_units_plural = sgqlc.types.Field(String, graphql_name='featureUnitsPlural')
    meter = sgqlc.types.Field(CreateMeter, graphql_name='meter')
    meter_type = sgqlc.types.Field(MeterType, graphql_name='meterType')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class FeatureSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(FeatureSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class FeatureStatusFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(FeatureStatus, graphql_name='eq')
    gt = sgqlc.types.Field(FeatureStatus, graphql_name='gt')
    gte = sgqlc.types.Field(FeatureStatus, graphql_name='gte')
    i_like = sgqlc.types.Field(FeatureStatus, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(FeatureStatus)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(FeatureStatus, graphql_name='like')
    lt = sgqlc.types.Field(FeatureStatus, graphql_name='lt')
    lte = sgqlc.types.Field(FeatureStatus, graphql_name='lte')
    neq = sgqlc.types.Field(FeatureStatus, graphql_name='neq')
    not_ilike = sgqlc.types.Field(FeatureStatus, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(FeatureStatus)), graphql_name='notIn')
    not_like = sgqlc.types.Field(FeatureStatus, graphql_name='notLike')


class FeatureTypeFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(FeatureType, graphql_name='eq')
    gt = sgqlc.types.Field(FeatureType, graphql_name='gt')
    gte = sgqlc.types.Field(FeatureType, graphql_name='gte')
    i_like = sgqlc.types.Field(FeatureType, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(FeatureType)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(FeatureType, graphql_name='like')
    lt = sgqlc.types.Field(FeatureType, graphql_name='lt')
    lte = sgqlc.types.Field(FeatureType, graphql_name='lte')
    neq = sgqlc.types.Field(FeatureType, graphql_name='neq')
    not_ilike = sgqlc.types.Field(FeatureType, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(FeatureType)), graphql_name='notIn')
    not_like = sgqlc.types.Field(FeatureType, graphql_name='notLike')


class FetchEntitlementQuery(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id', 'feature_id', 'options', 'resource_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    options = sgqlc.types.Field(EntitlementOptions, graphql_name='options')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class FetchEntitlementsQuery(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id', 'resource_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class FontVariantInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('font_size', 'font_weight')
    font_size = sgqlc.types.Field(Float, graphql_name='fontSize')
    font_weight = sgqlc.types.Field(FontWeight, graphql_name='fontWeight')


class GetActiveSubscriptionsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id', 'resource_id', 'resource_ids')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    resource_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='resourceIds')


class GetCustomerByRefIdInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')


class GetPackageByRefIdInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'ref_id', 'version_number')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    version_number = sgqlc.types.Field(Float, graphql_name='versionNumber')


class GetPaywallInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('billing_country_code', 'context', 'customer_id', 'environment_id', 'fetch_all_countries_prices', 'include_hidden_plans', 'product_id', 'resource_id')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    context = sgqlc.types.Field(WidgetType, graphql_name='context')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    fetch_all_countries_prices = sgqlc.types.Field(Boolean, graphql_name='fetchAllCountriesPrices')
    include_hidden_plans = sgqlc.types.Field(Boolean, graphql_name='includeHiddenPlans')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class GetWidgetConfigurationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id',)
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')


class GrantPromotionalEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('custom_end_date', 'feature_id', 'has_unlimited_usage', 'is_visible', 'monthly_reset_period_configuration', 'period', 'reset_period', 'usage_limit', 'weekly_reset_period_configuration', 'yearly_reset_period_configuration')
    custom_end_date = sgqlc.types.Field(DateTime, graphql_name='customEndDate')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    is_visible = sgqlc.types.Field(Boolean, graphql_name='isVisible')
    monthly_reset_period_configuration = sgqlc.types.Field('MonthlyResetPeriodConfigInput', graphql_name='monthlyResetPeriodConfiguration')
    period = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlementPeriod), graphql_name='period')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')
    yearly_reset_period_configuration = sgqlc.types.Field('YearlyResetPeriodConfigInput', graphql_name='yearlyResetPeriodConfiguration')


class GrantPromotionalEntitlementsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id', 'promotional_entitlements')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    promotional_entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(GrantPromotionalEntitlementInput))), graphql_name='promotionalEntitlements')


class HookFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'endpoint', 'environment_id', 'id', 'or_', 'status')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('HookFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    endpoint = sgqlc.types.Field('StringFieldComparison', graphql_name='endpoint')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('HookFilter')), graphql_name='or')
    status = sgqlc.types.Field('HookStatusFilterComparison', graphql_name='status')


class HookSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(HookSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class HookStatusFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(HookStatus, graphql_name='eq')
    gt = sgqlc.types.Field(HookStatus, graphql_name='gt')
    gte = sgqlc.types.Field(HookStatus, graphql_name='gte')
    i_like = sgqlc.types.Field(HookStatus, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(HookStatus)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(HookStatus, graphql_name='like')
    lt = sgqlc.types.Field(HookStatus, graphql_name='lt')
    lte = sgqlc.types.Field(HookStatus, graphql_name='lte')
    neq = sgqlc.types.Field(HookStatus, graphql_name='neq')
    not_ilike = sgqlc.types.Field(HookStatus, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(HookStatus)), graphql_name='notIn')
    not_like = sgqlc.types.Field(HookStatus, graphql_name='notLike')


class HubspotCredentialsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('authorization_code', 'refresh_token')
    authorization_code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='authorizationCode')
    refresh_token = sgqlc.types.Field(String, graphql_name='refreshToken')


class ImportCustomerBulk(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customers', 'environment_id')
    customers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ImportCustomerInput'))), graphql_name='customers')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')


class ImportCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'billing_id', 'customer_id', 'email', 'environment_id', 'name', 'payment_method_id', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    email = sgqlc.types.Field(String, graphql_name='email')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    name = sgqlc.types.Field(String, graphql_name='name')
    payment_method_id = sgqlc.types.Field(String, graphql_name='paymentMethodId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')


class ImportIntegrationCatalogInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('billing_model', 'entity_selection_mode', 'environment_id', 'feature_unit_name', 'feature_unit_plural_name', 'plans_selection_blacklist', 'plans_selection_whitelist', 'product_id', 'selected_addon_billing_ids', 'vendor_identifier')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    entity_selection_mode = sgqlc.types.Field(sgqlc.types.non_null(EntitySelectionMode), graphql_name='entitySelectionMode')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature_unit_name = sgqlc.types.Field(String, graphql_name='featureUnitName')
    feature_unit_plural_name = sgqlc.types.Field(String, graphql_name='featureUnitPluralName')
    plans_selection_blacklist = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='plansSelectionBlacklist')
    plans_selection_whitelist = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='plansSelectionWhitelist')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productId')
    selected_addon_billing_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='selectedAddonBillingIds')
    vendor_identifier = sgqlc.types.Field(sgqlc.types.non_null(VendorIdentifier), graphql_name='vendorIdentifier')


class ImportIntegrationCustomersInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customers_selection_blacklist', 'customers_selection_whitelist', 'entity_selection_mode', 'environment_id', 'product_id', 'vendor_identifier')
    customers_selection_blacklist = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='customersSelectionBlacklist')
    customers_selection_whitelist = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='customersSelectionWhitelist')
    entity_selection_mode = sgqlc.types.Field(sgqlc.types.non_null(EntitySelectionMode), graphql_name='entitySelectionMode')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productId')
    vendor_identifier = sgqlc.types.Field(sgqlc.types.non_null(VendorIdentifier), graphql_name='vendorIdentifier')


class ImportIntegrationTaskFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'environment_id', 'id', 'or_', 'status', 'task_type')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ImportIntegrationTaskFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ImportIntegrationTaskFilter')), graphql_name='or')
    status = sgqlc.types.Field('TaskStatusFilterComparison', graphql_name='status')
    task_type = sgqlc.types.Field('TaskTypeFilterComparison', graphql_name='taskType')


class ImportIntegrationTaskSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(ImportIntegrationTaskSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class ImportSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'billing_id', 'billing_period', 'customer_id', 'plan_id', 'resource_id', 'start_date', 'unit_quantity')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class ImportSubscriptionsBulk(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'subscriptions')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ImportSubscriptionInput))), graphql_name='subscriptions')


class InitAddStripeCustomerPaymentMethodInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_ref_id', 'environment_id')
    customer_ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerRefId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')


class IntFieldComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('between', 'eq', 'gt', 'gte', 'in_', 'is_', 'is_not', 'lt', 'lte', 'neq', 'not_between', 'not_in')
    between = sgqlc.types.Field('IntFieldComparisonBetween', graphql_name='between')
    eq = sgqlc.types.Field(Int, graphql_name='eq')
    gt = sgqlc.types.Field(Int, graphql_name='gt')
    gte = sgqlc.types.Field(Int, graphql_name='gte')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Int)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    lt = sgqlc.types.Field(Int, graphql_name='lt')
    lte = sgqlc.types.Field(Int, graphql_name='lte')
    neq = sgqlc.types.Field(Int, graphql_name='neq')
    not_between = sgqlc.types.Field('IntFieldComparisonBetween', graphql_name='notBetween')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Int)), graphql_name='notIn')


class IntFieldComparisonBetween(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('lower', 'upper')
    lower = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='lower')
    upper = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='upper')


class IntegrationFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'environment_id', 'id', 'or_', 'vendor_identifier')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('IntegrationFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('IntegrationFilter')), graphql_name='or')
    vendor_identifier = sgqlc.types.Field('VendorIdentifierFilterComparison', graphql_name='vendorIdentifier')


class IntegrationSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(IntegrationSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class ListAwsProductDimensionsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'product_id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productId')


class ListAwsProductsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id',)
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')


class MemberFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'id', 'or_')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('MemberFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('MemberFilter')), graphql_name='or')


class MemberSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(MemberSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class MergeEnvironmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('destination_environment_name', 'destination_environment_slug', 'migration_type', 'source_environment_slug', 'source_template')
    destination_environment_name = sgqlc.types.Field(String, graphql_name='destinationEnvironmentName')
    destination_environment_slug = sgqlc.types.Field(String, graphql_name='destinationEnvironmentSlug')
    migration_type = sgqlc.types.Field(PublishMigrationType, graphql_name='migrationType')
    source_environment_slug = sgqlc.types.Field(String, graphql_name='sourceEnvironmentSlug')
    source_template = sgqlc.types.Field(JSON, graphql_name='sourceTemplate')


class MeterAggregation(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('field', 'function')
    field = sgqlc.types.Field(String, graphql_name='field')
    function = sgqlc.types.Field(sgqlc.types.non_null(AggregationFunction), graphql_name='function')


class MeterConditionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('field', 'operation', 'value')
    field = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='field')
    operation = sgqlc.types.Field(sgqlc.types.non_null(ConditionOperation), graphql_name='operation')
    value = sgqlc.types.Field(String, graphql_name='value')


class MeterFilterDefinitionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('conditions',)
    conditions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MeterConditionInput))), graphql_name='conditions')


class MeterTypeFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(MeterType, graphql_name='eq')
    gt = sgqlc.types.Field(MeterType, graphql_name='gt')
    gte = sgqlc.types.Field(MeterType, graphql_name='gte')
    i_like = sgqlc.types.Field(MeterType, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(MeterType)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(MeterType, graphql_name='like')
    lt = sgqlc.types.Field(MeterType, graphql_name='lt')
    lte = sgqlc.types.Field(MeterType, graphql_name='lte')
    neq = sgqlc.types.Field(MeterType, graphql_name='neq')
    not_ilike = sgqlc.types.Field(MeterType, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(MeterType)), graphql_name='notIn')
    not_like = sgqlc.types.Field(MeterType, graphql_name='notLike')


class MoneyInputDTO(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('amount', 'currency')
    amount = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='amount')
    currency = sgqlc.types.Field(Currency, graphql_name='currency')


class MonthlyResetPeriodConfigInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('according_to',)
    according_to = sgqlc.types.Field(sgqlc.types.non_null(MonthlyAccordingTo), graphql_name='accordingTo')


class NumberFieldComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('between', 'eq', 'gt', 'gte', 'in_', 'is_', 'is_not', 'lt', 'lte', 'neq', 'not_between', 'not_in')
    between = sgqlc.types.Field('NumberFieldComparisonBetween', graphql_name='between')
    eq = sgqlc.types.Field(Float, graphql_name='eq')
    gt = sgqlc.types.Field(Float, graphql_name='gt')
    gte = sgqlc.types.Field(Float, graphql_name='gte')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Float)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    lt = sgqlc.types.Field(Float, graphql_name='lt')
    lte = sgqlc.types.Field(Float, graphql_name='lte')
    neq = sgqlc.types.Field(Float, graphql_name='neq')
    not_between = sgqlc.types.Field('NumberFieldComparisonBetween', graphql_name='notBetween')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Float)), graphql_name='notIn')


class NumberFieldComparisonBetween(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('lower', 'upper')
    lower = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='lower')
    upper = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='upper')


class OverageEntitlementCreateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('description', 'display_name_override', 'feature_id', 'has_unlimited_usage', 'hidden_from_widgets', 'is_custom', 'monthly_reset_period_configuration', 'order', 'reset_period', 'usage_limit', 'weekly_reset_period_configuration', 'yearly_reset_period_configuration')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name_override = sgqlc.types.Field(String, graphql_name='displayNameOverride')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    is_custom = sgqlc.types.Field(Boolean, graphql_name='isCustom')
    monthly_reset_period_configuration = sgqlc.types.Field(MonthlyResetPeriodConfigInput, graphql_name='monthlyResetPeriodConfiguration')
    order = sgqlc.types.Field(Float, graphql_name='order')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')
    yearly_reset_period_configuration = sgqlc.types.Field('YearlyResetPeriodConfigInput', graphql_name='yearlyResetPeriodConfiguration')


class OveragePricingModelCreateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('billing_model', 'entitlement', 'feature_id', 'price_periods')
    billing_model = sgqlc.types.Field(sgqlc.types.non_null(BillingModel), graphql_name='billingModel')
    entitlement = sgqlc.types.Field(OverageEntitlementCreateInput, graphql_name='entitlement')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    price_periods = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PricePeriodInput'))), graphql_name='pricePeriods')


class PackageDTOFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'or_', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageDTOFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    is_latest = sgqlc.types.Field(BooleanFieldComparison, graphql_name='isLatest')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageDTOFilter')), graphql_name='or')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='productId')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    status = sgqlc.types.Field('PackageStatusFilterComparison', graphql_name='status')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(IntFieldComparison, graphql_name='versionNumber')


class PackageDTOSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(PackageDTOSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class PackageEntitlementFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'environment_id', 'feature', 'id', 'or_', 'package', 'package_id', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlementFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    feature = sgqlc.types.Field('PackageEntitlementFilterFeatureFilter', graphql_name='feature')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlementFilter')), graphql_name='or')
    package = sgqlc.types.Field('PackageEntitlementFilterPackageDTOFilter', graphql_name='package')
    package_id = sgqlc.types.Field('StringFieldComparison', graphql_name='packageId')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class PackageEntitlementFilterFeatureFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'id', 'meter_type', 'or_', 'ref_id', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlementFilterFeatureFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    feature_status = sgqlc.types.Field(FeatureStatusFilterComparison, graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(FeatureTypeFilterComparison, graphql_name='featureType')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    meter_type = sgqlc.types.Field(MeterTypeFilterComparison, graphql_name='meterType')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlementFilterFeatureFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class PackageEntitlementFilterPackageDTOFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'or_', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlementFilterPackageDTOFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    is_latest = sgqlc.types.Field(BooleanFieldComparison, graphql_name='isLatest')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlementFilterPackageDTOFilter')), graphql_name='or')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='productId')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    status = sgqlc.types.Field('PackageStatusFilterComparison', graphql_name='status')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(IntFieldComparison, graphql_name='versionNumber')


class PackageEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('description', 'display_name_override', 'environment_id', 'feature_id', 'has_unlimited_usage', 'hidden_from_widgets', 'is_custom', 'monthly_reset_period_configuration', 'order', 'package_id', 'reset_period', 'usage_limit', 'weekly_reset_period_configuration', 'yearly_reset_period_configuration')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name_override = sgqlc.types.Field(String, graphql_name='displayNameOverride')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    is_custom = sgqlc.types.Field(Boolean, graphql_name='isCustom')
    monthly_reset_period_configuration = sgqlc.types.Field(MonthlyResetPeriodConfigInput, graphql_name='monthlyResetPeriodConfiguration')
    order = sgqlc.types.Field(Float, graphql_name='order')
    package_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='packageId')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')
    yearly_reset_period_configuration = sgqlc.types.Field('YearlyResetPeriodConfigInput', graphql_name='yearlyResetPeriodConfiguration')


class PackageEntitlementSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(PackageEntitlementSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class PackageEntitlementUpdateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('description', 'display_name_override', 'has_unlimited_usage', 'hidden_from_widgets', 'is_custom', 'monthly_reset_period_configuration', 'order', 'reset_period', 'usage_limit', 'weekly_reset_period_configuration', 'yearly_reset_period_configuration')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name_override = sgqlc.types.Field(String, graphql_name='displayNameOverride')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    is_custom = sgqlc.types.Field(Boolean, graphql_name='isCustom')
    monthly_reset_period_configuration = sgqlc.types.Field(MonthlyResetPeriodConfigInput, graphql_name='monthlyResetPeriodConfiguration')
    order = sgqlc.types.Field(Float, graphql_name='order')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')
    yearly_reset_period_configuration = sgqlc.types.Field('YearlyResetPeriodConfigInput', graphql_name='yearlyResetPeriodConfiguration')


class PackagePricingInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'overage_pricing_models', 'package_id', 'pricing_model', 'pricing_models', 'pricing_type')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    overage_pricing_models = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(OveragePricingModelCreateInput)), graphql_name='overagePricingModels')
    package_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='packageId')
    pricing_model = sgqlc.types.Field('PricingModelCreateInput', graphql_name='pricingModel')
    pricing_models = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PricingModelCreateInput')), graphql_name='pricingModels')
    pricing_type = sgqlc.types.Field(sgqlc.types.non_null(PricingType), graphql_name='pricingType')


class PackagePublishInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'migration_type')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    migration_type = sgqlc.types.Field(sgqlc.types.non_null(PublishMigrationType), graphql_name='migrationType')


class PackageStatusFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(PackageStatus, graphql_name='eq')
    gt = sgqlc.types.Field(PackageStatus, graphql_name='gt')
    gte = sgqlc.types.Field(PackageStatus, graphql_name='gte')
    i_like = sgqlc.types.Field(PackageStatus, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PackageStatus)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(PackageStatus, graphql_name='like')
    lt = sgqlc.types.Field(PackageStatus, graphql_name='lt')
    lte = sgqlc.types.Field(PackageStatus, graphql_name='lte')
    neq = sgqlc.types.Field(PackageStatus, graphql_name='neq')
    not_ilike = sgqlc.types.Field(PackageStatus, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PackageStatus)), graphql_name='notIn')
    not_like = sgqlc.types.Field(PackageStatus, graphql_name='notLike')


class PaymentCollectionFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(PaymentCollection, graphql_name='eq')
    gt = sgqlc.types.Field(PaymentCollection, graphql_name='gt')
    gte = sgqlc.types.Field(PaymentCollection, graphql_name='gte')
    i_like = sgqlc.types.Field(PaymentCollection, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PaymentCollection)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(PaymentCollection, graphql_name='like')
    lt = sgqlc.types.Field(PaymentCollection, graphql_name='lt')
    lte = sgqlc.types.Field(PaymentCollection, graphql_name='lte')
    neq = sgqlc.types.Field(PaymentCollection, graphql_name='neq')
    not_ilike = sgqlc.types.Field(PaymentCollection, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PaymentCollection)), graphql_name='notIn')
    not_like = sgqlc.types.Field(PaymentCollection, graphql_name='notLike')


class PaywallColorsPaletteInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('background_color', 'border_color', 'current_plan_background', 'primary', 'text_color')
    background_color = sgqlc.types.Field(String, graphql_name='backgroundColor')
    border_color = sgqlc.types.Field(String, graphql_name='borderColor')
    current_plan_background = sgqlc.types.Field(String, graphql_name='currentPlanBackground')
    primary = sgqlc.types.Field(String, graphql_name='primary')
    text_color = sgqlc.types.Field(String, graphql_name='textColor')


class PaywallConfigurationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('custom_css', 'layout', 'palette', 'typography')
    custom_css = sgqlc.types.Field(String, graphql_name='customCss')
    layout = sgqlc.types.Field('PaywallLayoutConfigurationInput', graphql_name='layout')
    palette = sgqlc.types.Field(PaywallColorsPaletteInput, graphql_name='palette')
    typography = sgqlc.types.Field('TypographyConfigurationInput', graphql_name='typography')


class PaywallLayoutConfigurationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('alignment', 'plan_margin', 'plan_padding', 'plan_width')
    alignment = sgqlc.types.Field(Alignment, graphql_name='alignment')
    plan_margin = sgqlc.types.Field(Float, graphql_name='planMargin')
    plan_padding = sgqlc.types.Field(Float, graphql_name='planPadding')
    plan_width = sgqlc.types.Field(Float, graphql_name='planWidth')


class PlanCreateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'aws_marketplace_plan_dimension', 'billing_id', 'description', 'display_name', 'environment_id', 'hidden_from_widgets', 'parent_plan_id', 'pricing_type', 'product_id', 'ref_id', 'status')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    aws_marketplace_plan_dimension = sgqlc.types.Field(String, graphql_name='awsMarketplacePlanDimension')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    parent_plan_id = sgqlc.types.Field(String, graphql_name='parentPlanId')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')


class PlanFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'compatible_addons', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'or_', 'pricing_type', 'product', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PlanFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    compatible_addons = sgqlc.types.Field('PlanFilterAddonFilter', graphql_name='compatibleAddons')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    is_latest = sgqlc.types.Field(BooleanFieldComparison, graphql_name='isLatest')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PlanFilter')), graphql_name='or')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    product = sgqlc.types.Field('PlanFilterProductFilter', graphql_name='product')
    product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='productId')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    status = sgqlc.types.Field(PackageStatusFilterComparison, graphql_name='status')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(IntFieldComparison, graphql_name='versionNumber')


class PlanFilterAddonFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'or_', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PlanFilterAddonFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    is_latest = sgqlc.types.Field(BooleanFieldComparison, graphql_name='isLatest')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PlanFilterAddonFilter')), graphql_name='or')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='productId')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    status = sgqlc.types.Field(PackageStatusFilterComparison, graphql_name='status')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(IntFieldComparison, graphql_name='versionNumber')


class PlanFilterProductFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'aws_marketplace_product_code', 'aws_marketplace_product_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_default_product', 'or_', 'ref_id', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PlanFilterProductFilter')), graphql_name='and')
    aws_marketplace_product_code = sgqlc.types.Field('StringFieldComparison', graphql_name='awsMarketplaceProductCode')
    aws_marketplace_product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='awsMarketplaceProductId')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    is_default_product = sgqlc.types.Field(BooleanFieldComparison, graphql_name='isDefaultProduct')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PlanFilterProductFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class PlanSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(PlanSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class PlanUpdateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'billing_id', 'default_trial_config', 'description', 'display_name', 'hidden_from_widgets', 'id', 'parent_plan_id', 'status')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    default_trial_config = sgqlc.types.Field(DefaultTrialConfigInputDTO, graphql_name='defaultTrialConfig')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    parent_plan_id = sgqlc.types.Field(String, graphql_name='parentPlanId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')


class PreviewSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('addons', 'billable_features', 'billing_country_code', 'billing_information', 'billing_period', 'customer_id', 'environment_id', 'plan_id', 'promotion_code', 'resource_id', 'start_date', 'unit_quantity')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonInput')), graphql_name='addons')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillableFeatureInput)), graphql_name='billableFeatures')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_information = sgqlc.types.Field('SubscriptionBillingInfo', graphql_name='billingInformation')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')
    promotion_code = sgqlc.types.Field(String, graphql_name='promotionCode')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class PriceFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'billing_model', 'billing_period', 'created_at', 'id', 'or_', 'package', 'tiers_mode')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PriceFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    billing_model = sgqlc.types.Field(BillingModelFilterComparison, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(BillingPeriodFilterComparison, graphql_name='billingPeriod')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PriceFilter')), graphql_name='or')
    package = sgqlc.types.Field('PriceFilterPackageDTOFilter', graphql_name='package')
    tiers_mode = sgqlc.types.Field('TiersModeFilterComparison', graphql_name='tiersMode')


class PriceFilterPackageDTOFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'or_', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PriceFilterPackageDTOFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field('StringFieldComparison', graphql_name='billingId')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    is_latest = sgqlc.types.Field(BooleanFieldComparison, graphql_name='isLatest')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PriceFilterPackageDTOFilter')), graphql_name='or')
    pricing_type = sgqlc.types.Field('PricingTypeFilterComparison', graphql_name='pricingType')
    product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='productId')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    status = sgqlc.types.Field(PackageStatusFilterComparison, graphql_name='status')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(IntFieldComparison, graphql_name='versionNumber')


class PricePeriodInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('billing_country_code', 'billing_period', 'price', 'tiers')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_period = sgqlc.types.Field(sgqlc.types.non_null(BillingPeriod), graphql_name='billingPeriod')
    price = sgqlc.types.Field(MoneyInputDTO, graphql_name='price')
    tiers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PriceTierInput')), graphql_name='tiers')


class PriceSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(PriceSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class PriceTierInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('flat_price', 'unit_price', 'up_to')
    flat_price = sgqlc.types.Field(MoneyInputDTO, graphql_name='flatPrice')
    unit_price = sgqlc.types.Field(MoneyInputDTO, graphql_name='unitPrice')
    up_to = sgqlc.types.Field(Float, graphql_name='upTo')


class PricingModelCreateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('billing_model', 'feature_id', 'max_unit_quantity', 'min_unit_quantity', 'price_periods', 'tiers_mode')
    billing_model = sgqlc.types.Field(sgqlc.types.non_null(BillingModel), graphql_name='billingModel')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    max_unit_quantity = sgqlc.types.Field(Float, graphql_name='maxUnitQuantity')
    min_unit_quantity = sgqlc.types.Field(Float, graphql_name='minUnitQuantity')
    price_periods = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PricePeriodInput))), graphql_name='pricePeriods')
    tiers_mode = sgqlc.types.Field(TiersMode, graphql_name='tiersMode')


class PricingTypeFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(PricingType, graphql_name='eq')
    gt = sgqlc.types.Field(PricingType, graphql_name='gt')
    gte = sgqlc.types.Field(PricingType, graphql_name='gte')
    i_like = sgqlc.types.Field(PricingType, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PricingType)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(PricingType, graphql_name='like')
    lt = sgqlc.types.Field(PricingType, graphql_name='lt')
    lte = sgqlc.types.Field(PricingType, graphql_name='lte')
    neq = sgqlc.types.Field(PricingType, graphql_name='neq')
    not_ilike = sgqlc.types.Field(PricingType, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PricingType)), graphql_name='notIn')
    not_like = sgqlc.types.Field(PricingType, graphql_name='notLike')


class ProductCreateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'description', 'display_name', 'environment_id', 'multiple_subscriptions', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    multiple_subscriptions = sgqlc.types.Field(Boolean, graphql_name='multipleSubscriptions')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class ProductFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'aws_marketplace_product_code', 'aws_marketplace_product_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_default_product', 'or_', 'ref_id', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ProductFilter')), graphql_name='and')
    aws_marketplace_product_code = sgqlc.types.Field('StringFieldComparison', graphql_name='awsMarketplaceProductCode')
    aws_marketplace_product_id = sgqlc.types.Field('StringFieldComparison', graphql_name='awsMarketplaceProductId')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field('StringFieldComparison', graphql_name='description')
    display_name = sgqlc.types.Field('StringFieldComparison', graphql_name='displayName')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    is_default_product = sgqlc.types.Field(BooleanFieldComparison, graphql_name='isDefaultProduct')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ProductFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field('StringFieldComparison', graphql_name='refId')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class ProductSettingsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('downgrade_at_end_of_billing_period', 'downgrade_plan_id', 'subscription_cancellation_time', 'subscription_end_setup', 'subscription_start_plan_id', 'subscription_start_setup')
    downgrade_at_end_of_billing_period = sgqlc.types.Field(String, graphql_name='downgradeAtEndOfBillingPeriod')
    downgrade_plan_id = sgqlc.types.Field(String, graphql_name='downgradePlanId')
    subscription_cancellation_time = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionCancellationTime), graphql_name='subscriptionCancellationTime')
    subscription_end_setup = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionEndSetup), graphql_name='subscriptionEndSetup')
    subscription_start_plan_id = sgqlc.types.Field(String, graphql_name='subscriptionStartPlanId')
    subscription_start_setup = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionStartSetup), graphql_name='subscriptionStartSetup')


class ProductSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(ProductSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class ProductUpdateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'description', 'display_name', 'multiple_subscriptions', 'product_settings')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    multiple_subscriptions = sgqlc.types.Field(Boolean, graphql_name='multipleSubscriptions')
    product_settings = sgqlc.types.Field(ProductSettingsInput, graphql_name='productSettings')


class PromotionalEntitlementFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'environment_id', 'id', 'or_', 'status', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PromotionalEntitlementFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    environment_id = sgqlc.types.Field('StringFieldComparison', graphql_name='environmentId')
    id = sgqlc.types.Field('StringFieldComparison', graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PromotionalEntitlementFilter')), graphql_name='or')
    status = sgqlc.types.Field('PromotionalEntitlementStatusFilterComparison', graphql_name='status')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class PromotionalEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'description', 'end_date', 'environment_id', 'feature_id', 'has_unlimited_usage', 'is_visible', 'monthly_reset_period_configuration', 'period', 'reset_period', 'usage_limit', 'weekly_reset_period_configuration', 'yearly_reset_period_configuration')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    description = sgqlc.types.Field(String, graphql_name='description')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    is_visible = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isVisible')
    monthly_reset_period_configuration = sgqlc.types.Field(MonthlyResetPeriodConfigInput, graphql_name='monthlyResetPeriodConfiguration')
    period = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlementPeriod), graphql_name='period')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')
    yearly_reset_period_configuration = sgqlc.types.Field('YearlyResetPeriodConfigInput', graphql_name='yearlyResetPeriodConfiguration')


class PromotionalEntitlementSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlementSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class PromotionalEntitlementStatusFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='eq')
    gt = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='gt')
    gte = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='gte')
    i_like = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PromotionalEntitlementStatus)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='like')
    lt = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='lt')
    lte = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='lte')
    neq = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='neq')
    not_ilike = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PromotionalEntitlementStatus)), graphql_name='notIn')
    not_like = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='notLike')


class PromotionalEntitlementUpdateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('description', 'end_date', 'has_unlimited_usage', 'is_visible', 'monthly_reset_period_configuration', 'period', 'reset_period', 'usage_limit', 'weekly_reset_period_configuration')
    description = sgqlc.types.Field(String, graphql_name='description')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    is_visible = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isVisible')
    monthly_reset_period_configuration = sgqlc.types.Field(MonthlyResetPeriodConfigInput, graphql_name='monthlyResetPeriodConfiguration')
    period = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlementPeriod), graphql_name='period')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')


class ProvisionCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'aws_marketplace_customer_id', 'billing_id', 'billing_information', 'coupon_ref_id', 'created_at', 'crm_id', 'customer_id', 'email', 'environment_id', 'exclude_from_experiment', 'name', 'ref_id', 'should_sync_free', 'subscription_params')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    aws_marketplace_customer_id = sgqlc.types.Field(String, graphql_name='awsMarketplaceCustomerId')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_information = sgqlc.types.Field(CustomerBillingInfo, graphql_name='billingInformation')
    coupon_ref_id = sgqlc.types.Field(String, graphql_name='couponRefId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    email = sgqlc.types.Field(String, graphql_name='email')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    exclude_from_experiment = sgqlc.types.Field(Boolean, graphql_name='excludeFromExperiment')
    name = sgqlc.types.Field(String, graphql_name='name')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    should_sync_free = sgqlc.types.Field(Boolean, graphql_name='shouldSyncFree')
    subscription_params = sgqlc.types.Field('ProvisionCustomerSubscriptionInput', graphql_name='subscriptionParams')


class ProvisionCustomerSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'addons', 'await_payment_confirmation', 'billable_features', 'billing_country_code', 'billing_id', 'billing_information', 'billing_period', 'plan_id', 'price_unit_amount', 'promotion_code', 'ref_id', 'resource_id', 'start_date', 'subscription_entitlements', 'subscription_id', 'trial_override_configuration', 'unit_quantity')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonInput')), graphql_name='addons')
    await_payment_confirmation = sgqlc.types.Field(Boolean, graphql_name='awaitPaymentConfirmation')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillableFeatureInput)), graphql_name='billableFeatures')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_information = sgqlc.types.Field('SubscriptionBillingInfo', graphql_name='billingInformation')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')
    price_unit_amount = sgqlc.types.Field(Float, graphql_name='priceUnitAmount')
    promotion_code = sgqlc.types.Field(String, graphql_name='promotionCode')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    subscription_entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementInput')), graphql_name='subscriptionEntitlements')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    trial_override_configuration = sgqlc.types.Field('TrialOverrideConfigurationInput', graphql_name='trialOverrideConfiguration')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class ProvisionSandboxInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('billing_model', 'display_name')
    billing_model = sgqlc.types.Field(sgqlc.types.non_null(BillingModel), graphql_name='billingModel')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')


class ProvisionSubscription(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'addons', 'await_payment_confirmation', 'billable_features', 'billing_country_code', 'billing_id', 'billing_information', 'billing_period', 'checkout_options', 'customer_id', 'plan_id', 'price_unit_amount', 'promotion_code', 'ref_id', 'resource_id', 'skip_trial', 'start_date', 'subscription_entitlements', 'subscription_id', 'trial_override_configuration', 'unit_quantity')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonInput')), graphql_name='addons')
    await_payment_confirmation = sgqlc.types.Field(Boolean, graphql_name='awaitPaymentConfirmation')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillableFeatureInput)), graphql_name='billableFeatures')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_information = sgqlc.types.Field('SubscriptionBillingInfo', graphql_name='billingInformation')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    checkout_options = sgqlc.types.Field(CheckoutOptions, graphql_name='checkoutOptions')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')
    price_unit_amount = sgqlc.types.Field(Float, graphql_name='priceUnitAmount')
    promotion_code = sgqlc.types.Field(String, graphql_name='promotionCode')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    skip_trial = sgqlc.types.Field(Boolean, graphql_name='skipTrial')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    subscription_entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementInput')), graphql_name='subscriptionEntitlements')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    trial_override_configuration = sgqlc.types.Field('TrialOverrideConfigurationInput', graphql_name='trialOverrideConfiguration')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class ProvisionSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'addons', 'await_payment_confirmation', 'billable_features', 'billing_country_code', 'billing_id', 'billing_information', 'billing_period', 'checkout_options', 'customer_id', 'plan_id', 'price_unit_amount', 'promotion_code', 'ref_id', 'resource_id', 'skip_trial', 'start_date', 'subscription_entitlements', 'subscription_id', 'trial_override_configuration', 'unit_quantity')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonInput')), graphql_name='addons')
    await_payment_confirmation = sgqlc.types.Field(Boolean, graphql_name='awaitPaymentConfirmation')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillableFeatureInput)), graphql_name='billableFeatures')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_information = sgqlc.types.Field('SubscriptionBillingInfo', graphql_name='billingInformation')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    checkout_options = sgqlc.types.Field(CheckoutOptions, graphql_name='checkoutOptions')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')
    price_unit_amount = sgqlc.types.Field(Float, graphql_name='priceUnitAmount')
    promotion_code = sgqlc.types.Field(String, graphql_name='promotionCode')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    skip_trial = sgqlc.types.Field(Boolean, graphql_name='skipTrial')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    subscription_entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementInput')), graphql_name='subscriptionEntitlements')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    trial_override_configuration = sgqlc.types.Field('TrialOverrideConfigurationInput', graphql_name='trialOverrideConfiguration')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class RecalculateEntitlementsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_ids', 'environment_id', 'for_all_customers')
    customer_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='customerIds')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    for_all_customers = sgqlc.types.Field(Boolean, graphql_name='forAllCustomers')


class RemoveBasePlanFromPlanInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class RemoveCompatibleAddonsFromPlanInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_ids')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='relationIds')


class RemoveCouponFromCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class RemoveCouponFromCustomerSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class RemoveExperimentFromCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class RemoveExperimentFromCustomerSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class ReportUsageBaseInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('created_at', 'customer_id', 'feature_id', 'resource_id', 'update_behavior', 'value')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    update_behavior = sgqlc.types.Field(UsageUpdateBehavior, graphql_name='updateBehavior')
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class ReportUsageBulkInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'usages')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    usages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ReportUsageBaseInput))), graphql_name='usages')


class ReportUsageInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('created_at', 'customer_id', 'environment_id', 'feature_id', 'resource_id', 'update_behavior', 'value')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    update_behavior = sgqlc.types.Field(UsageUpdateBehavior, graphql_name='updateBehavior')
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class ResyncIntegrationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'vendor_identifier')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    vendor_identifier = sgqlc.types.Field(sgqlc.types.non_null(VendorIdentifier), graphql_name='vendorIdentifier')


class RevokePromotionalEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id', 'feature_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')


class SetBasePlanOnPlanInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class SetCompatibleAddonsOnPlanInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_ids')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='relationIds')


class SetCouponOnCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class SetCouponOnCustomerSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class SetExperimentOnCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class SetExperimentOnCustomerSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'relation_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    relation_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='relationId')


class StartExperimentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'ref_id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class StopExperimentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'ref_id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class StringFieldComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(String, graphql_name='eq')
    gt = sgqlc.types.Field(String, graphql_name='gt')
    gte = sgqlc.types.Field(String, graphql_name='gte')
    i_like = sgqlc.types.Field(String, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(String, graphql_name='like')
    lt = sgqlc.types.Field(String, graphql_name='lt')
    lte = sgqlc.types.Field(String, graphql_name='lte')
    neq = sgqlc.types.Field(String, graphql_name='neq')
    not_ilike = sgqlc.types.Field(String, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='notIn')
    not_like = sgqlc.types.Field(String, graphql_name='notLike')


class StripeCredentialsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('account_id', 'authorization_code', 'is_test_mode')
    account_id = sgqlc.types.Field(String, graphql_name='accountId')
    authorization_code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='authorizationCode')
    is_test_mode = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isTestMode')


class StripeCustomerSearchInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_name', 'environment_id', 'next_page')
    customer_name = sgqlc.types.Field(String, graphql_name='customerName')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    next_page = sgqlc.types.Field(String, graphql_name='nextPage')


class StripeProductSearchInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'next_page', 'product_name')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    next_page = sgqlc.types.Field(String, graphql_name='nextPage')
    product_name = sgqlc.types.Field(String, graphql_name='productName')


class StripeSubscriptionSearchInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'next_page')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    next_page = sgqlc.types.Field(String, graphql_name='nextPage')


class SubscriptionAddonFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('addon', 'and_', 'created_at', 'id', 'or_', 'price', 'quantity', 'subscription', 'updated_at')
    addon = sgqlc.types.Field('SubscriptionAddonFilterAddonFilter', graphql_name='addon')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonFilter')), graphql_name='or')
    price = sgqlc.types.Field('SubscriptionAddonFilterPriceFilter', graphql_name='price')
    quantity = sgqlc.types.Field(NumberFieldComparison, graphql_name='quantity')
    subscription = sgqlc.types.Field('SubscriptionAddonFilterCustomerSubscriptionFilter', graphql_name='subscription')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class SubscriptionAddonFilterAddonFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'or_', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonFilterAddonFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field(StringFieldComparison, graphql_name='description')
    display_name = sgqlc.types.Field(StringFieldComparison, graphql_name='displayName')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    is_latest = sgqlc.types.Field(BooleanFieldComparison, graphql_name='isLatest')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonFilterAddonFilter')), graphql_name='or')
    pricing_type = sgqlc.types.Field(PricingTypeFilterComparison, graphql_name='pricingType')
    product_id = sgqlc.types.Field(StringFieldComparison, graphql_name='productId')
    ref_id = sgqlc.types.Field(StringFieldComparison, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatusFilterComparison, graphql_name='status')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(IntFieldComparison, graphql_name='versionNumber')


class SubscriptionAddonFilterCustomerSubscriptionFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'or_', 'payment_collection', 'pricing_type', 'ref_id', 'resource_id', 'start_date', 'status', 'subscription_id', 'trial_end_date')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonFilterCustomerSubscriptionFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='billingId')
    cancel_reason = sgqlc.types.Field('SubscriptionCancelReasonFilterComparison', graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field(DateFieldComparison, graphql_name='cancellationDate')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(StringFieldComparison, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(StringFieldComparison, graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field(DateFieldComparison, graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field(DateFieldComparison, graphql_name='currentBillingPeriodStart')
    effective_end_date = sgqlc.types.Field(DateFieldComparison, graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field(DateFieldComparison, graphql_name='endDate')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    old_billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='oldBillingId')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonFilterCustomerSubscriptionFilter')), graphql_name='or')
    payment_collection = sgqlc.types.Field(PaymentCollectionFilterComparison, graphql_name='paymentCollection')
    pricing_type = sgqlc.types.Field(PricingTypeFilterComparison, graphql_name='pricingType')
    ref_id = sgqlc.types.Field(StringFieldComparison, graphql_name='refId')
    resource_id = sgqlc.types.Field(StringFieldComparison, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateFieldComparison, graphql_name='startDate')
    status = sgqlc.types.Field('SubscriptionStatusFilterComparison', graphql_name='status')
    subscription_id = sgqlc.types.Field(StringFieldComparison, graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field(DateFieldComparison, graphql_name='trialEndDate')


class SubscriptionAddonFilterPriceFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'billing_model', 'billing_period', 'created_at', 'id', 'or_', 'tiers_mode')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonFilterPriceFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='billingId')
    billing_model = sgqlc.types.Field(BillingModelFilterComparison, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(BillingPeriodFilterComparison, graphql_name='billingPeriod')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddonFilterPriceFilter')), graphql_name='or')
    tiers_mode = sgqlc.types.Field('TiersModeFilterComparison', graphql_name='tiersMode')


class SubscriptionAddonInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('addon_id', 'quantity')
    addon_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='addonId')
    quantity = sgqlc.types.Field(Int, graphql_name='quantity')


class SubscriptionAddonSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionAddonSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class SubscriptionBillingInfo(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('billing_address', 'charge_on_behalf_of_account', 'coupon_id', 'is_backdated', 'is_invoice_paid', 'metadata', 'tax_percentage', 'tax_rate_ids')
    billing_address = sgqlc.types.Field(BillingAddress, graphql_name='billingAddress')
    charge_on_behalf_of_account = sgqlc.types.Field(String, graphql_name='chargeOnBehalfOfAccount')
    coupon_id = sgqlc.types.Field(String, graphql_name='couponId')
    is_backdated = sgqlc.types.Field(Boolean, graphql_name='isBackdated')
    is_invoice_paid = sgqlc.types.Field(Boolean, graphql_name='isInvoicePaid')
    metadata = sgqlc.types.Field(JSON, graphql_name='metadata')
    tax_percentage = sgqlc.types.Field(Float, graphql_name='taxPercentage')
    tax_rate_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='taxRateIds')


class SubscriptionCancelReasonFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='eq')
    gt = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='gt')
    gte = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='gte')
    i_like = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionCancelReason)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='like')
    lt = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='lt')
    lte = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='lte')
    neq = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='neq')
    not_ilike = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionCancelReason)), graphql_name='notIn')
    not_like = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='notLike')


class SubscriptionCancellationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('end_date', 'environment_id', 'subscription_cancellation_action', 'subscription_cancellation_time', 'subscription_ref_id')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    subscription_cancellation_action = sgqlc.types.Field(SubscriptionCancellationAction, graphql_name='subscriptionCancellationAction')
    subscription_cancellation_time = sgqlc.types.Field(SubscriptionCancellationTime, graphql_name='subscriptionCancellationTime')
    subscription_ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subscriptionRefId')


class SubscriptionEntitlementFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'environment_id', 'feature', 'id', 'or_', 'subscription', 'subscription_id', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    feature = sgqlc.types.Field('SubscriptionEntitlementFilterFeatureFilter', graphql_name='feature')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementFilter')), graphql_name='or')
    subscription = sgqlc.types.Field('SubscriptionEntitlementFilterCustomerSubscriptionFilter', graphql_name='subscription')
    subscription_id = sgqlc.types.Field(StringFieldComparison, graphql_name='subscriptionId')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class SubscriptionEntitlementFilterCustomerSubscriptionFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'or_', 'payment_collection', 'pricing_type', 'ref_id', 'resource_id', 'start_date', 'status', 'subscription_id', 'trial_end_date')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementFilterCustomerSubscriptionFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='billingId')
    cancel_reason = sgqlc.types.Field(SubscriptionCancelReasonFilterComparison, graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field(DateFieldComparison, graphql_name='cancellationDate')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(StringFieldComparison, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(StringFieldComparison, graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field(DateFieldComparison, graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field(DateFieldComparison, graphql_name='currentBillingPeriodStart')
    effective_end_date = sgqlc.types.Field(DateFieldComparison, graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field(DateFieldComparison, graphql_name='endDate')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    old_billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='oldBillingId')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementFilterCustomerSubscriptionFilter')), graphql_name='or')
    payment_collection = sgqlc.types.Field(PaymentCollectionFilterComparison, graphql_name='paymentCollection')
    pricing_type = sgqlc.types.Field(PricingTypeFilterComparison, graphql_name='pricingType')
    ref_id = sgqlc.types.Field(StringFieldComparison, graphql_name='refId')
    resource_id = sgqlc.types.Field(StringFieldComparison, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateFieldComparison, graphql_name='startDate')
    status = sgqlc.types.Field('SubscriptionStatusFilterComparison', graphql_name='status')
    subscription_id = sgqlc.types.Field(StringFieldComparison, graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field(DateFieldComparison, graphql_name='trialEndDate')


class SubscriptionEntitlementFilterFeatureFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'id', 'meter_type', 'or_', 'ref_id', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementFilterFeatureFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field(StringFieldComparison, graphql_name='description')
    display_name = sgqlc.types.Field(StringFieldComparison, graphql_name='displayName')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    feature_status = sgqlc.types.Field(FeatureStatusFilterComparison, graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(FeatureTypeFilterComparison, graphql_name='featureType')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    meter_type = sgqlc.types.Field(MeterTypeFilterComparison, graphql_name='meterType')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementFilterFeatureFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field(StringFieldComparison, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class SubscriptionEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('description', 'feature_id', 'has_unlimited_usage', 'monthly_reset_period_configuration', 'reset_period', 'usage_limit', 'weekly_reset_period_configuration', 'yearly_reset_period_configuration')
    description = sgqlc.types.Field(String, graphql_name='description')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    monthly_reset_period_configuration = sgqlc.types.Field(MonthlyResetPeriodConfigInput, graphql_name='monthlyResetPeriodConfiguration')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')
    yearly_reset_period_configuration = sgqlc.types.Field('YearlyResetPeriodConfigInput', graphql_name='yearlyResetPeriodConfiguration')


class SubscriptionEntitlementSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionEntitlementSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class SubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'addons', 'await_payment_confirmation', 'billable_features', 'billing_country_code', 'billing_id', 'billing_information', 'billing_period', 'crm_id', 'customer_id', 'end_date', 'environment_id', 'is_custom_price_subscription', 'is_overriding_trial_config', 'is_trial', 'plan_id', 'price_unit_amount', 'promotion_code', 'ref_id', 'resource_id', 'start_date', 'subscription_entitlements', 'subscription_id', 'unit_quantity')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionAddonInput)), graphql_name='addons')
    await_payment_confirmation = sgqlc.types.Field(Boolean, graphql_name='awaitPaymentConfirmation')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillableFeatureInput)), graphql_name='billableFeatures')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_information = sgqlc.types.Field(SubscriptionBillingInfo, graphql_name='billingInformation')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    is_custom_price_subscription = sgqlc.types.Field(Boolean, graphql_name='isCustomPriceSubscription')
    is_overriding_trial_config = sgqlc.types.Field(Boolean, graphql_name='isOverridingTrialConfig')
    is_trial = sgqlc.types.Field(Boolean, graphql_name='isTrial')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')
    price_unit_amount = sgqlc.types.Field(Float, graphql_name='priceUnitAmount')
    promotion_code = sgqlc.types.Field(String, graphql_name='promotionCode')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    subscription_entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionEntitlementInput)), graphql_name='subscriptionEntitlements')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class SubscriptionMigrationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'subscription_id', 'subscription_migration_time')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    subscription_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subscriptionId')
    subscription_migration_time = sgqlc.types.Field(SubscriptionMigrationTime, graphql_name='subscriptionMigrationTime')


class SubscriptionMigrationTaskFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'environment_id', 'id', 'or_', 'status', 'task_type')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionMigrationTaskFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionMigrationTaskFilter')), graphql_name='or')
    status = sgqlc.types.Field('TaskStatusFilterComparison', graphql_name='status')
    task_type = sgqlc.types.Field('TaskTypeFilterComparison', graphql_name='taskType')


class SubscriptionMigrationTaskSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionMigrationTaskSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class SubscriptionPriceFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_model', 'created_at', 'feature_id', 'id', 'or_', 'price', 'subscription', 'updated_at', 'usage_limit')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionPriceFilter')), graphql_name='and')
    billing_model = sgqlc.types.Field(BillingModelFilterComparison, graphql_name='billingModel')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    feature_id = sgqlc.types.Field(StringFieldComparison, graphql_name='featureId')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionPriceFilter')), graphql_name='or')
    price = sgqlc.types.Field('SubscriptionPriceFilterPriceFilter', graphql_name='price')
    subscription = sgqlc.types.Field('SubscriptionPriceFilterCustomerSubscriptionFilter', graphql_name='subscription')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(NumberFieldComparison, graphql_name='usageLimit')


class SubscriptionPriceFilterCustomerSubscriptionFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'or_', 'payment_collection', 'pricing_type', 'ref_id', 'resource_id', 'start_date', 'status', 'subscription_id', 'trial_end_date')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionPriceFilterCustomerSubscriptionFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='billingId')
    cancel_reason = sgqlc.types.Field(SubscriptionCancelReasonFilterComparison, graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field(DateFieldComparison, graphql_name='cancellationDate')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(StringFieldComparison, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(StringFieldComparison, graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field(DateFieldComparison, graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field(DateFieldComparison, graphql_name='currentBillingPeriodStart')
    effective_end_date = sgqlc.types.Field(DateFieldComparison, graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field(DateFieldComparison, graphql_name='endDate')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    old_billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='oldBillingId')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionPriceFilterCustomerSubscriptionFilter')), graphql_name='or')
    payment_collection = sgqlc.types.Field(PaymentCollectionFilterComparison, graphql_name='paymentCollection')
    pricing_type = sgqlc.types.Field(PricingTypeFilterComparison, graphql_name='pricingType')
    ref_id = sgqlc.types.Field(StringFieldComparison, graphql_name='refId')
    resource_id = sgqlc.types.Field(StringFieldComparison, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateFieldComparison, graphql_name='startDate')
    status = sgqlc.types.Field('SubscriptionStatusFilterComparison', graphql_name='status')
    subscription_id = sgqlc.types.Field(StringFieldComparison, graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field(DateFieldComparison, graphql_name='trialEndDate')


class SubscriptionPriceFilterPriceFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'billing_model', 'billing_period', 'created_at', 'id', 'or_', 'tiers_mode')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionPriceFilterPriceFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='billingId')
    billing_model = sgqlc.types.Field(BillingModelFilterComparison, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(BillingPeriodFilterComparison, graphql_name='billingPeriod')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionPriceFilterPriceFilter')), graphql_name='or')
    tiers_mode = sgqlc.types.Field('TiersModeFilterComparison', graphql_name='tiersMode')


class SubscriptionPriceSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionPriceSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class SubscriptionStatusFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(SubscriptionStatus, graphql_name='eq')
    gt = sgqlc.types.Field(SubscriptionStatus, graphql_name='gt')
    gte = sgqlc.types.Field(SubscriptionStatus, graphql_name='gte')
    i_like = sgqlc.types.Field(SubscriptionStatus, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionStatus)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(SubscriptionStatus, graphql_name='like')
    lt = sgqlc.types.Field(SubscriptionStatus, graphql_name='lt')
    lte = sgqlc.types.Field(SubscriptionStatus, graphql_name='lte')
    neq = sgqlc.types.Field(SubscriptionStatus, graphql_name='neq')
    not_ilike = sgqlc.types.Field(SubscriptionStatus, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionStatus)), graphql_name='notIn')
    not_like = sgqlc.types.Field(SubscriptionStatus, graphql_name='notLike')


class SubscriptionUpdateScheduleCancellationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'status', 'subscription_id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    status = sgqlc.types.Field(SubscriptionScheduleStatus, graphql_name='status')
    subscription_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subscriptionId')


class SyncTaxRatesInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id',)
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')


class TaskStatusFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(TaskStatus, graphql_name='eq')
    gt = sgqlc.types.Field(TaskStatus, graphql_name='gt')
    gte = sgqlc.types.Field(TaskStatus, graphql_name='gte')
    i_like = sgqlc.types.Field(TaskStatus, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TaskStatus)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(TaskStatus, graphql_name='like')
    lt = sgqlc.types.Field(TaskStatus, graphql_name='lt')
    lte = sgqlc.types.Field(TaskStatus, graphql_name='lte')
    neq = sgqlc.types.Field(TaskStatus, graphql_name='neq')
    not_ilike = sgqlc.types.Field(TaskStatus, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TaskStatus)), graphql_name='notIn')
    not_like = sgqlc.types.Field(TaskStatus, graphql_name='notLike')


class TaskTypeFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(TaskType, graphql_name='eq')
    gt = sgqlc.types.Field(TaskType, graphql_name='gt')
    gte = sgqlc.types.Field(TaskType, graphql_name='gte')
    i_like = sgqlc.types.Field(TaskType, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TaskType)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(TaskType, graphql_name='like')
    lt = sgqlc.types.Field(TaskType, graphql_name='lt')
    lte = sgqlc.types.Field(TaskType, graphql_name='lte')
    neq = sgqlc.types.Field(TaskType, graphql_name='neq')
    not_ilike = sgqlc.types.Field(TaskType, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TaskType)), graphql_name='notIn')
    not_like = sgqlc.types.Field(TaskType, graphql_name='notLike')


class TaxExempt(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('type', 'value')
    type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='type')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')


class TestHookInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('endpoint_url', 'environment_id', 'hook_event_type')
    endpoint_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='endpointUrl')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    hook_event_type = sgqlc.types.Field(sgqlc.types.non_null(EventLogType), graphql_name='hookEventType')


class TiersModeFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(TiersMode, graphql_name='eq')
    gt = sgqlc.types.Field(TiersMode, graphql_name='gt')
    gte = sgqlc.types.Field(TiersMode, graphql_name='gte')
    i_like = sgqlc.types.Field(TiersMode, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TiersMode)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(TiersMode, graphql_name='like')
    lt = sgqlc.types.Field(TiersMode, graphql_name='lt')
    lte = sgqlc.types.Field(TiersMode, graphql_name='lte')
    neq = sgqlc.types.Field(TiersMode, graphql_name='neq')
    not_ilike = sgqlc.types.Field(TiersMode, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(TiersMode)), graphql_name='notIn')
    not_like = sgqlc.types.Field(TiersMode, graphql_name='notLike')


class TransferSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'destination_resource_id', 'source_resource_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    destination_resource_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='destinationResourceId')
    source_resource_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourceResourceId')


class TrialOverrideConfigurationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('is_trial', 'trial_end_date')
    is_trial = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isTrial')
    trial_end_date = sgqlc.types.Field(DateTime, graphql_name='trialEndDate')


class TriggerSubscriptionMigrationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'ref_id', 'version_number')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    version_number = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='versionNumber')


class TypographyConfigurationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('body', 'font_family', 'h1', 'h2', 'h3')
    body = sgqlc.types.Field(FontVariantInput, graphql_name='body')
    font_family = sgqlc.types.Field(String, graphql_name='fontFamily')
    h1 = sgqlc.types.Field(FontVariantInput, graphql_name='h1')
    h2 = sgqlc.types.Field(FontVariantInput, graphql_name='h2')
    h3 = sgqlc.types.Field(FontVariantInput, graphql_name='h3')


class UnarchiveCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'environment_id')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')


class UnarchiveEnvironmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'slug')
    id = sgqlc.types.Field(String, graphql_name='id')
    slug = sgqlc.types.Field(String, graphql_name='slug')


class UpdateAccountInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('display_name', 'id', 'subscription_billing_anchor', 'subscription_proration_behavior', 'timezone')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    id = sgqlc.types.Field(String, graphql_name='id')
    subscription_billing_anchor = sgqlc.types.Field(BillingAnchor, graphql_name='subscriptionBillingAnchor')
    subscription_proration_behavior = sgqlc.types.Field(ProrationBehavior, graphql_name='subscriptionProrationBehavior')
    timezone = sgqlc.types.Field(String, graphql_name='timezone')


class UpdateCouponInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'description', 'environment_id', 'name', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    description = sgqlc.types.Field(String, graphql_name='description')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class UpdateCustomerInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'aws_marketplace_customer_id', 'billing_id', 'billing_information', 'coupon_ref_id', 'crm_id', 'customer_id', 'email', 'environment_id', 'name', 'ref_id', 'should_wait_sync')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    aws_marketplace_customer_id = sgqlc.types.Field(String, graphql_name='awsMarketplaceCustomerId')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_information = sgqlc.types.Field(CustomerBillingInfo, graphql_name='billingInformation')
    coupon_ref_id = sgqlc.types.Field(String, graphql_name='couponRefId')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    email = sgqlc.types.Field(String, graphql_name='email')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    name = sgqlc.types.Field(String, graphql_name='name')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    should_wait_sync = sgqlc.types.Field(Boolean, graphql_name='shouldWaitSync')


class UpdateExperimentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('control_group_name', 'description', 'environment_id', 'name', 'product_id', 'product_settings', 'ref_id', 'variant_group_name', 'variant_percentage')
    control_group_name = sgqlc.types.Field(String, graphql_name='controlGroupName')
    description = sgqlc.types.Field(String, graphql_name='description')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    name = sgqlc.types.Field(String, graphql_name='name')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    product_settings = sgqlc.types.Field(ProductSettingsInput, graphql_name='productSettings')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    variant_group_name = sgqlc.types.Field(String, graphql_name='variantGroupName')
    variant_percentage = sgqlc.types.Field(Float, graphql_name='variantPercentage')


class UpdateFeature(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'created_at', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'feature_units', 'feature_units_plural', 'id', 'meter_type', 'ref_id', 'updated_at')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_status = sgqlc.types.Field(FeatureStatus, graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(FeatureType, graphql_name='featureType')
    feature_units = sgqlc.types.Field(String, graphql_name='featureUnits')
    feature_units_plural = sgqlc.types.Field(String, graphql_name='featureUnitsPlural')
    id = sgqlc.types.Field(String, graphql_name='id')
    meter_type = sgqlc.types.Field(MeterType, graphql_name='meterType')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class UpdateFeatureInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'description', 'display_name', 'environment_id', 'feature_units', 'feature_units_plural', 'meter', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature_units = sgqlc.types.Field(String, graphql_name='featureUnits')
    feature_units_plural = sgqlc.types.Field(String, graphql_name='featureUnitsPlural')
    meter = sgqlc.types.Field(CreateMeter, graphql_name='meter')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class UpdateHook(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'endpoint', 'environment_id', 'event_log_types', 'id', 'secret_key', 'status')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    endpoint = sgqlc.types.Field(String, graphql_name='endpoint')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    event_log_types = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(EventLogType)), graphql_name='eventLogTypes')
    id = sgqlc.types.Field(String, graphql_name='id')
    secret_key = sgqlc.types.Field(String, graphql_name='secretKey')
    status = sgqlc.types.Field(HookStatus, graphql_name='status')


class UpdateIntegrationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('stripe_credentials', 'vendor_identifier', 'zuora_credentials')
    stripe_credentials = sgqlc.types.Field(StripeCredentialsInput, graphql_name='stripeCredentials')
    vendor_identifier = sgqlc.types.Field(sgqlc.types.non_null(VendorIdentifier), graphql_name='vendorIdentifier')
    zuora_credentials = sgqlc.types.Field('ZuoraCredentialsInput', graphql_name='zuoraCredentials')


class UpdateOneEnvironmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'update')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    update = sgqlc.types.Field(sgqlc.types.non_null(EnvironmentInput), graphql_name='update')


class UpdateOneFeatureInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'update')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    update = sgqlc.types.Field(sgqlc.types.non_null(UpdateFeature), graphql_name='update')


class UpdateOneHookInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'update')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    update = sgqlc.types.Field(sgqlc.types.non_null(UpdateHook), graphql_name='update')


class UpdateOneIntegrationInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'update')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    update = sgqlc.types.Field(sgqlc.types.non_null(UpdateIntegrationInput), graphql_name='update')


class UpdateOnePackageEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'update')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    update = sgqlc.types.Field(sgqlc.types.non_null(PackageEntitlementUpdateInput), graphql_name='update')


class UpdateOneProductInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'update')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    update = sgqlc.types.Field(sgqlc.types.non_null(ProductUpdateInput), graphql_name='update')


class UpdateOnePromotionalEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'update')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    update = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlementUpdateInput), graphql_name='update')


class UpdatePackageEntitlementOrderInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('entitlements', 'environment_id', 'package_id')
    entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UpdatePackageEntitlementOrderItemInput'))), graphql_name='entitlements')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    package_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='packageId')


class UpdatePackageEntitlementOrderItemInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('id', 'order')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    order = sgqlc.types.Field(Float, graphql_name='order')


class UpdateSubscriptionEntitlementInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('feature_id', 'has_unlimited_usage', 'id', 'monthly_reset_period_configuration', 'reset_period', 'usage_limit', 'weekly_reset_period_configuration', 'yearly_reset_period_configuration')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    id = sgqlc.types.Field(String, graphql_name='id')
    monthly_reset_period_configuration = sgqlc.types.Field(MonthlyResetPeriodConfigInput, graphql_name='monthlyResetPeriodConfiguration')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')
    yearly_reset_period_configuration = sgqlc.types.Field('YearlyResetPeriodConfigInput', graphql_name='yearlyResetPeriodConfiguration')


class UpdateSubscriptionInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'addons', 'await_payment_confirmation', 'billable_features', 'billing_information', 'billing_period', 'environment_id', 'promotion_code', 'ref_id', 'subscription_entitlements', 'subscription_id', 'trial_end_date', 'unit_quantity')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionAddonInput)), graphql_name='addons')
    await_payment_confirmation = sgqlc.types.Field(Boolean, graphql_name='awaitPaymentConfirmation')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillableFeatureInput)), graphql_name='billableFeatures')
    billing_information = sgqlc.types.Field(SubscriptionBillingInfo, graphql_name='billingInformation')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    promotion_code = sgqlc.types.Field(String, graphql_name='promotionCode')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    subscription_entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(UpdateSubscriptionEntitlementInput)), graphql_name='subscriptionEntitlements')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field(DateTime, graphql_name='trialEndDate')
    unit_quantity = sgqlc.types.Field(Float, graphql_name='unitQuantity')


class UpdateUserInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('department', 'name')
    department = sgqlc.types.Field(Department, graphql_name='department')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class UsageEventReportInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_id', 'dimensions', 'event_name', 'idempotency_key', 'resource_id', 'timestamp')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    dimensions = sgqlc.types.Field(JSON, graphql_name='dimensions')
    event_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='eventName')
    idempotency_key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='idempotencyKey')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    timestamp = sgqlc.types.Field(DateTime, graphql_name='timestamp')


class UsageEventsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'filters')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    filters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(MeterFilterDefinitionInput)), graphql_name='filters')


class UsageEventsReportInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('environment_id', 'usage_events')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    usage_events = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UsageEventReportInput))), graphql_name='usageEvents')


class UsageHistoryInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('customer_ref_id', 'end_date', 'environment_id', 'feature_ref_id', 'monthly_reset_period_configuration', 'reset_period', 'resource_ref_id', 'start_date', 'weekly_reset_period_configuration', 'yearly_reset_period_configuration')
    customer_ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerRefId')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureRefId')
    monthly_reset_period_configuration = sgqlc.types.Field(MonthlyResetPeriodConfigInput, graphql_name='monthlyResetPeriodConfiguration')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    resource_ref_id = sgqlc.types.Field(String, graphql_name='resourceRefId')
    start_date = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='startDate')
    weekly_reset_period_configuration = sgqlc.types.Field('WeeklyResetPeriodConfigInput', graphql_name='weeklyResetPeriodConfiguration')
    yearly_reset_period_configuration = sgqlc.types.Field('YearlyResetPeriodConfigInput', graphql_name='yearlyResetPeriodConfiguration')


class UsageMeasurementCreateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('created_at', 'customer_id', 'environment_id', 'feature_id', 'resource_id', 'update_behavior', 'value')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    update_behavior = sgqlc.types.Field(UsageUpdateBehavior, graphql_name='updateBehavior')
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class UsageMeasurementFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'customer', 'environment_id', 'feature', 'id', 'or_')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UsageMeasurementFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    customer = sgqlc.types.Field('UsageMeasurementFilterCustomerFilter', graphql_name='customer')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    feature = sgqlc.types.Field('UsageMeasurementFilterFeatureFilter', graphql_name='feature')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UsageMeasurementFilter')), graphql_name='or')


class UsageMeasurementFilterCustomerFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'or_', 'ref_id', 'search_query', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UsageMeasurementFilterCustomerFilter')), graphql_name='and')
    billing_id = sgqlc.types.Field(StringFieldComparison, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field(StringFieldComparison, graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field(StringFieldComparison, graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field(StringFieldComparison, graphql_name='crmId')
    customer_id = sgqlc.types.Field(StringFieldComparison, graphql_name='customerId')
    deleted_at = sgqlc.types.Field(DateFieldComparison, graphql_name='deletedAt')
    email = sgqlc.types.Field(StringFieldComparison, graphql_name='email')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    name = sgqlc.types.Field(StringFieldComparison, graphql_name='name')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UsageMeasurementFilterCustomerFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field(StringFieldComparison, graphql_name='refId')
    search_query = sgqlc.types.Field(CustomerSearchQueryFilterComparison, graphql_name='searchQuery')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class UsageMeasurementFilterFeatureFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('and_', 'created_at', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'id', 'meter_type', 'or_', 'ref_id', 'updated_at')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UsageMeasurementFilterFeatureFilter')), graphql_name='and')
    created_at = sgqlc.types.Field(DateFieldComparison, graphql_name='createdAt')
    description = sgqlc.types.Field(StringFieldComparison, graphql_name='description')
    display_name = sgqlc.types.Field(StringFieldComparison, graphql_name='displayName')
    environment_id = sgqlc.types.Field(StringFieldComparison, graphql_name='environmentId')
    feature_status = sgqlc.types.Field(FeatureStatusFilterComparison, graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(FeatureTypeFilterComparison, graphql_name='featureType')
    id = sgqlc.types.Field(StringFieldComparison, graphql_name='id')
    meter_type = sgqlc.types.Field(MeterTypeFilterComparison, graphql_name='meterType')
    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UsageMeasurementFilterFeatureFilter')), graphql_name='or')
    ref_id = sgqlc.types.Field(StringFieldComparison, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateFieldComparison, graphql_name='updatedAt')


class UsageMeasurementSort(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('direction', 'field', 'nulls')
    direction = sgqlc.types.Field(sgqlc.types.non_null(SortDirection), graphql_name='direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(UsageMeasurementSortFields), graphql_name='field')
    nulls = sgqlc.types.Field(SortNulls, graphql_name='nulls')


class ValidateMergeEnvironmentInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('destination_environment_slug', 'source_environment_slug')
    destination_environment_slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='destinationEnvironmentSlug')
    source_environment_slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='sourceEnvironmentSlug')


class VendorIdentifierFilterComparison(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('eq', 'gt', 'gte', 'i_like', 'in_', 'is_', 'is_not', 'like', 'lt', 'lte', 'neq', 'not_ilike', 'not_in', 'not_like')
    eq = sgqlc.types.Field(VendorIdentifier, graphql_name='eq')
    gt = sgqlc.types.Field(VendorIdentifier, graphql_name='gt')
    gte = sgqlc.types.Field(VendorIdentifier, graphql_name='gte')
    i_like = sgqlc.types.Field(VendorIdentifier, graphql_name='iLike')
    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(VendorIdentifier)), graphql_name='in')
    is_ = sgqlc.types.Field(Boolean, graphql_name='is')
    is_not = sgqlc.types.Field(Boolean, graphql_name='isNot')
    like = sgqlc.types.Field(VendorIdentifier, graphql_name='like')
    lt = sgqlc.types.Field(VendorIdentifier, graphql_name='lt')
    lte = sgqlc.types.Field(VendorIdentifier, graphql_name='lte')
    neq = sgqlc.types.Field(VendorIdentifier, graphql_name='neq')
    not_ilike = sgqlc.types.Field(VendorIdentifier, graphql_name='notILike')
    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(VendorIdentifier)), graphql_name='notIn')
    not_like = sgqlc.types.Field(VendorIdentifier, graphql_name='notLike')


class WeeklyResetPeriodConfigInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('according_to',)
    according_to = sgqlc.types.Field(sgqlc.types.non_null(WeeklyAccordingTo), graphql_name='accordingTo')


class WidgetConfigurationUpdateInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('checkout_configuration', 'customer_portal_configuration', 'environment_id', 'paywall_configuration')
    checkout_configuration = sgqlc.types.Field(CheckoutConfigurationInput, graphql_name='checkoutConfiguration')
    customer_portal_configuration = sgqlc.types.Field(CustomerPortalConfigurationInput, graphql_name='customerPortalConfiguration')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    paywall_configuration = sgqlc.types.Field(PaywallConfigurationInput, graphql_name='paywallConfiguration')


class YearlyResetPeriodConfigInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('according_to',)
    according_to = sgqlc.types.Field(sgqlc.types.non_null(YearlyAccordingTo), graphql_name='accordingTo')


class ZuoraCredentialsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ('base_url', 'client_id', 'client_secret')
    base_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='baseUrl')
    client_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='clientId')
    client_secret = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='clientSecret')



########################################################################
# Output Objects and Interfaces
########################################################################
class Account(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account_email_domain', 'account_status', 'display_name', 'id', 'saml_enabled', 'subscription_billing_anchor', 'subscription_proration_behavior', 'timezone')
    account_email_domain = sgqlc.types.Field(String, graphql_name='accountEmailDomain')
    account_status = sgqlc.types.Field(AccountStatus, graphql_name='accountStatus')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    saml_enabled = sgqlc.types.Field(Boolean, graphql_name='samlEnabled')
    subscription_billing_anchor = sgqlc.types.Field(BillingAnchor, graphql_name='subscriptionBillingAnchor')
    subscription_proration_behavior = sgqlc.types.Field(ProrationBehavior, graphql_name='subscriptionProrationBehavior')
    timezone = sgqlc.types.Field(String, graphql_name='timezone')


class AccountNotFoundError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class AdditionalMetaDataChange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'change_type')
    after = sgqlc.types.Field(JSON, graphql_name='after')
    before = sgqlc.types.Field(JSON, graphql_name='before')
    change_type = sgqlc.types.Field(ChangeType, graphql_name='changeType')


class Addon(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'billing_id', 'billing_link_url', 'created_at', 'description', 'display_name', 'draft_details', 'draft_summary', 'entitlements', 'environment', 'environment_id', 'hidden_from_widgets', 'id', 'is_latest', 'overage_prices', 'prices', 'pricing_type', 'product', 'product_id', 'ref_id', 'status', 'sync_states', 'type', 'updated_at', 'version_number')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_link_url = sgqlc.types.Field(String, graphql_name='billingLinkUrl')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    draft_details = sgqlc.types.Field('PackageDraftDetails', graphql_name='draftDetails')
    draft_summary = sgqlc.types.Field('PackageDraftSummary', graphql_name='draftSummary')
    entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlement')), graphql_name='entitlements')
    environment = sgqlc.types.Field(sgqlc.types.non_null('Environment'), graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_latest = sgqlc.types.Field(Boolean, graphql_name='isLatest')
    overage_prices = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Price')), graphql_name='overagePrices')
    prices = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Price')), graphql_name='prices', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(PriceFilter, graphql_name='filter', default={})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(PriceSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product = sgqlc.types.Field('Product', graphql_name='product')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    status = sgqlc.types.Field(sgqlc.types.non_null(PackageStatus), graphql_name='status')
    sync_states = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SyncState')), graphql_name='syncStates')
    type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='type')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='versionNumber')


class AddonAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    is_latest = sgqlc.types.Field(Boolean, graphql_name='isLatest')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(Int, graphql_name='versionNumber')


class AddonAvgAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('version_number',)
    version_number = sgqlc.types.Field(Float, graphql_name='versionNumber')


class AddonChangeVariables(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('addon_ref_id', 'new_quantity')
    addon_ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='addonRefId')
    new_quantity = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='newQuantity')


class AddonConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AddonEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class AddonCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    billing_id = sgqlc.types.Field(Int, graphql_name='billingId')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    description = sgqlc.types.Field(Int, graphql_name='description')
    display_name = sgqlc.types.Field(Int, graphql_name='displayName')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    is_latest = sgqlc.types.Field(Int, graphql_name='isLatest')
    pricing_type = sgqlc.types.Field(Int, graphql_name='pricingType')
    product_id = sgqlc.types.Field(Int, graphql_name='productId')
    ref_id = sgqlc.types.Field(Int, graphql_name='refId')
    status = sgqlc.types.Field(Int, graphql_name='status')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(Int, graphql_name='versionNumber')


class AddonDeleteResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'billing_id', 'billing_link_url', 'created_at', 'description', 'display_name', 'draft_details', 'draft_summary', 'entitlements', 'environment_id', 'hidden_from_widgets', 'id', 'is_latest', 'overage_prices', 'prices', 'pricing_type', 'product_id', 'ref_id', 'status', 'sync_states', 'type', 'updated_at', 'version_number')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_link_url = sgqlc.types.Field(String, graphql_name='billingLinkUrl')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    draft_details = sgqlc.types.Field('PackageDraftDetails', graphql_name='draftDetails')
    draft_summary = sgqlc.types.Field('PackageDraftSummary', graphql_name='draftSummary')
    entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlement')), graphql_name='entitlements')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    id = sgqlc.types.Field(String, graphql_name='id')
    is_latest = sgqlc.types.Field(Boolean, graphql_name='isLatest')
    overage_prices = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Price')), graphql_name='overagePrices')
    prices = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Price')), graphql_name='prices')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')
    sync_states = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SyncState')), graphql_name='syncStates')
    type = sgqlc.types.Field(String, graphql_name='type')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(Int, graphql_name='versionNumber')


class AddonEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Addon), graphql_name='node')


class AddonMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(Int, graphql_name='versionNumber')


class AddonMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(Int, graphql_name='versionNumber')


class AddonSumAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('version_number',)
    version_number = sgqlc.types.Field(Float, graphql_name='versionNumber')


class AggregatedEventsByCustomer(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('aggregated_usage',)
    aggregated_usage = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CustomerAggregatedUsage'))), graphql_name='aggregatedUsage')


class Aggregation(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('field', 'function')
    field = sgqlc.types.Field(String, graphql_name='field')
    function = sgqlc.types.Field(sgqlc.types.non_null(AggregationFunction), graphql_name='function')


class ApiKey(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id', 'key_type', 'token')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    key_type = sgqlc.types.Field(sgqlc.types.non_null(ApiKeyType), graphql_name='keyType')
    token = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='token')


class ApplySubscription(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('entitlements', 'subscription')
    entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Entitlement')), graphql_name='entitlements')
    subscription = sgqlc.types.Field('CustomerSubscription', graphql_name='subscription')


class AsyncTaskResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('task_id',)
    task_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='taskId')


class AwsDimension(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('description', 'key', 'name', 'stigg_plan_id', 'stigg_plan_name', 'type', 'unit')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    stigg_plan_id = sgqlc.types.Field(String, graphql_name='stiggPlanId')
    stigg_plan_name = sgqlc.types.Field(String, graphql_name='stiggPlanName')
    type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='type')
    unit = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='unit')


class AwsMarketplaceCredentials(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('aws_role_arn',)
    aws_role_arn = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='awsRoleArn')


class AwsProduct(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('description', 'logo_url', 'product_code', 'product_id', 'stigg_product_id', 'stigg_product_ref_id', 'title', 'visibility')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    logo_url = sgqlc.types.Field(String, graphql_name='logoUrl')
    product_code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productCode')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productId')
    stigg_product_id = sgqlc.types.Field(String, graphql_name='stiggProductId')
    stigg_product_ref_id = sgqlc.types.Field(String, graphql_name='stiggProductRefId')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    visibility = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='visibility')


class BaseError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code',)
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')


class BasePlanChange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'change_type')
    after = sgqlc.types.Field(Addon, graphql_name='after')
    before = sgqlc.types.Field(Addon, graphql_name='before')
    change_type = sgqlc.types.Field(ChangeType, graphql_name='changeType')


class BillableFeature(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('feature_id', 'quantity')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    quantity = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='quantity')


class BillingPeriodChangeVariables(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_period',)
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')


class CannotDeleteCustomerError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class CannotDeleteFeatureError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class CheckoutBillingIntegration(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_identifier', 'credentials')
    billing_identifier = sgqlc.types.Field(sgqlc.types.non_null(BillingVendorIdentifier), graphql_name='billingIdentifier')
    credentials = sgqlc.types.Field(sgqlc.types.non_null('CheckoutCredentials'), graphql_name='credentials')


class CheckoutColorPalette(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('background_color', 'border_color', 'primary', 'summary_background_color', 'text_color')
    background_color = sgqlc.types.Field(String, graphql_name='backgroundColor')
    border_color = sgqlc.types.Field(String, graphql_name='borderColor')
    primary = sgqlc.types.Field(String, graphql_name='primary')
    summary_background_color = sgqlc.types.Field(String, graphql_name='summaryBackgroundColor')
    text_color = sgqlc.types.Field(String, graphql_name='textColor')


class CheckoutConfiguration(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('content', 'custom_css', 'palette', 'typography')
    content = sgqlc.types.Field('CheckoutContent', graphql_name='content')
    custom_css = sgqlc.types.Field(String, graphql_name='customCss')
    palette = sgqlc.types.Field(CheckoutColorPalette, graphql_name='palette')
    typography = sgqlc.types.Field('TypographyConfiguration', graphql_name='typography')


class CheckoutContent(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('collect_phone_number',)
    collect_phone_number = sgqlc.types.Field(Boolean, graphql_name='collectPhoneNumber')


class CheckoutCredentials(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account_id', 'public_key')
    account_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='accountId')
    public_key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='publicKey')


class CheckoutState(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('active_subscription', 'billing_integration', 'configuration', 'customer', 'plan', 'resource', 'setup_secret')
    active_subscription = sgqlc.types.Field('CustomerSubscription', graphql_name='activeSubscription')
    billing_integration = sgqlc.types.Field(sgqlc.types.non_null(CheckoutBillingIntegration), graphql_name='billingIntegration')
    configuration = sgqlc.types.Field(CheckoutConfiguration, graphql_name='configuration')
    customer = sgqlc.types.Field(sgqlc.types.non_null('Customer'), graphql_name='customer')
    plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='plan')
    resource = sgqlc.types.Field('CustomerResource', graphql_name='resource')
    setup_secret = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='setupSecret')


class Coupon(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'billing_id', 'billing_link_url', 'created_at', 'customers', 'description', 'discount_value', 'environment', 'environment_id', 'id', 'name', 'ref_id', 'status', 'sync_states', 'type', 'updated_at')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_link_url = sgqlc.types.Field(String, graphql_name='billingLinkUrl')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdAt')
    customers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Customer')), graphql_name='customers', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(CustomerFilter, graphql_name='filter', default={})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(CustomerSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    description = sgqlc.types.Field(String, graphql_name='description')
    discount_value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='discountValue')
    environment = sgqlc.types.Field('Environment', graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    status = sgqlc.types.Field(sgqlc.types.non_null(CouponStatus), graphql_name='status')
    sync_states = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SyncState')), graphql_name='syncStates')
    type = sgqlc.types.Field(sgqlc.types.non_null(CouponType), graphql_name='type')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')


class CouponAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'environment_id', 'id', 'name', 'ref_id', 'status', 'type', 'updated_at')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(CouponStatus, graphql_name='status')
    type = sgqlc.types.Field(CouponType, graphql_name='type')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class CouponAvgAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(Float, graphql_name='id')


class CouponConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CouponEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class CouponCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'environment_id', 'id', 'name', 'ref_id', 'status', 'type', 'updated_at')
    billing_id = sgqlc.types.Field(Int, graphql_name='billingId')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    description = sgqlc.types.Field(Int, graphql_name='description')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    name = sgqlc.types.Field(Int, graphql_name='name')
    ref_id = sgqlc.types.Field(Int, graphql_name='refId')
    status = sgqlc.types.Field(Int, graphql_name='status')
    type = sgqlc.types.Field(Int, graphql_name='type')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')


class CouponEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Coupon), graphql_name='node')


class CouponMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'environment_id', 'id', 'name', 'ref_id', 'status', 'type', 'updated_at')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(CouponStatus, graphql_name='status')
    type = sgqlc.types.Field(CouponType, graphql_name='type')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class CouponMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'environment_id', 'id', 'name', 'ref_id', 'status', 'type', 'updated_at')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(CouponStatus, graphql_name='status')
    type = sgqlc.types.Field(CouponType, graphql_name='type')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class CouponSumAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(Float, graphql_name='id')


class Customer(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'aws_marketplace_customer_id', 'billing_currency', 'billing_id', 'billing_link_url', 'coupon', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'default_payment_expiration_month', 'default_payment_expiration_year', 'default_payment_method_id', 'default_payment_method_last4_digits', 'default_payment_method_type', 'deleted_at', 'eligible_for_trial', 'email', 'environment', 'environment_id', 'exclude_from_experiment', 'experiment', 'experiment_info', 'has_active_resource', 'has_active_subscription', 'has_payment_method', 'id', 'name', 'promotional_entitlements', 'ref_id', 'statistics', 'subscriptions', 'sync_states', 'total_active_promotional_entitlements', 'total_active_subscription', 'trialed_plans', 'updated_at')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    aws_marketplace_customer_id = sgqlc.types.Field(String, graphql_name='awsMarketplaceCustomerId')
    billing_currency = sgqlc.types.Field(Currency, graphql_name='billingCurrency')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_link_url = sgqlc.types.Field(String, graphql_name='billingLinkUrl')
    coupon = sgqlc.types.Field(Coupon, graphql_name='coupon')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field(String, graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field(String, graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    default_payment_expiration_month = sgqlc.types.Field(Int, graphql_name='defaultPaymentExpirationMonth')
    default_payment_expiration_year = sgqlc.types.Field(Int, graphql_name='defaultPaymentExpirationYear')
    default_payment_method_id = sgqlc.types.Field(String, graphql_name='defaultPaymentMethodId')
    default_payment_method_last4_digits = sgqlc.types.Field(String, graphql_name='defaultPaymentMethodLast4Digits')
    default_payment_method_type = sgqlc.types.Field(PaymentMethodType, graphql_name='defaultPaymentMethodType')
    deleted_at = sgqlc.types.Field(DateTime, graphql_name='deletedAt')
    eligible_for_trial = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('EligibleForTrial')), graphql_name='eligibleForTrial')
    email = sgqlc.types.Field(String, graphql_name='email')
    environment = sgqlc.types.Field('Environment', graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    exclude_from_experiment = sgqlc.types.Field(Boolean, graphql_name='excludeFromExperiment')
    experiment = sgqlc.types.Field('Experiment', graphql_name='experiment')
    experiment_info = sgqlc.types.Field('experimentInfo', graphql_name='experimentInfo')
    has_active_resource = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasActiveResource')
    has_active_subscription = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasActiveSubscription')
    has_payment_method = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasPaymentMethod')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    promotional_entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PromotionalEntitlement'))), graphql_name='promotionalEntitlements', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(PromotionalEntitlementFilter, graphql_name='filter', default={})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(PromotionalEntitlementSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    statistics = sgqlc.types.Field('CustomerStatistics', graphql_name='statistics')
    subscriptions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscription')), graphql_name='subscriptions', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(CustomerSubscriptionFilter, graphql_name='filter', default={'status': {'in': ['ACTIVE', 'IN_TRIAL']}})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(CustomerSubscriptionSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    sync_states = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SyncState')), graphql_name='syncStates')
    total_active_promotional_entitlements = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='totalActivePromotionalEntitlements')
    total_active_subscription = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='totalActiveSubscription')
    trialed_plans = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('TrialedPlan')), graphql_name='trialedPlans')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')


class CustomerAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'ref_id', 'search_query', 'updated_at')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field(String, graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field(String, graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    deleted_at = sgqlc.types.Field(DateTime, graphql_name='deletedAt')
    email = sgqlc.types.Field(String, graphql_name='email')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    search_query = sgqlc.types.Field(String, graphql_name='searchQuery')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class CustomerAggregatedUsage(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('customer_id', 'usage')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    usage = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='usage')


class CustomerConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CustomerEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class CustomerCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'ref_id', 'search_query', 'updated_at')
    billing_id = sgqlc.types.Field(Int, graphql_name='billingId')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field(Int, graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field(Int, graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field(Int, graphql_name='crmId')
    customer_id = sgqlc.types.Field(Int, graphql_name='customerId')
    deleted_at = sgqlc.types.Field(Int, graphql_name='deletedAt')
    email = sgqlc.types.Field(Int, graphql_name='email')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    name = sgqlc.types.Field(Int, graphql_name='name')
    ref_id = sgqlc.types.Field(Int, graphql_name='refId')
    search_query = sgqlc.types.Field(Int, graphql_name='searchQuery')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')


class CustomerEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='node')


class CustomerMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'ref_id', 'search_query', 'updated_at')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field(String, graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field(String, graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    deleted_at = sgqlc.types.Field(DateTime, graphql_name='deletedAt')
    email = sgqlc.types.Field(String, graphql_name='email')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    search_query = sgqlc.types.Field(String, graphql_name='searchQuery')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class CustomerMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'crm_hubspot_company_id', 'crm_hubspot_company_url', 'crm_id', 'customer_id', 'deleted_at', 'email', 'environment_id', 'id', 'name', 'ref_id', 'search_query', 'updated_at')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_hubspot_company_id = sgqlc.types.Field(String, graphql_name='crmHubspotCompanyId')
    crm_hubspot_company_url = sgqlc.types.Field(String, graphql_name='crmHubspotCompanyUrl')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    deleted_at = sgqlc.types.Field(DateTime, graphql_name='deletedAt')
    email = sgqlc.types.Field(String, graphql_name='email')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    search_query = sgqlc.types.Field(String, graphql_name='searchQuery')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class CustomerNoBillingId(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class CustomerNotFoundError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class CustomerPortal(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_information', 'billing_portal_url', 'can_upgrade_subscription', 'configuration', 'entitlements', 'promotional_entitlements', 'resource', 'show_watermark', 'subscriptions')
    billing_information = sgqlc.types.Field(sgqlc.types.non_null('CustomerPortalBillingInformation'), graphql_name='billingInformation')
    billing_portal_url = sgqlc.types.Field(String, graphql_name='billingPortalUrl')
    can_upgrade_subscription = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canUpgradeSubscription')
    configuration = sgqlc.types.Field('CustomerPortalConfiguration', graphql_name='configuration')
    entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Entitlement'))), graphql_name='entitlements')
    promotional_entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CustomerPortalPromotionalEntitlement'))), graphql_name='promotionalEntitlements')
    resource = sgqlc.types.Field('CustomerResource', graphql_name='resource')
    show_watermark = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='showWatermark')
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CustomerPortalSubscription'))), graphql_name='subscriptions')


class CustomerPortalAddon(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('addon_id', 'description', 'display_name', 'quantity')
    addon_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='addonId')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    quantity = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='quantity')


class CustomerPortalBillingInformation(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('default_payment_expiration_month', 'default_payment_expiration_year', 'default_payment_method_id', 'default_payment_method_last4_digits', 'default_payment_method_type', 'email', 'name')
    default_payment_expiration_month = sgqlc.types.Field(Int, graphql_name='defaultPaymentExpirationMonth')
    default_payment_expiration_year = sgqlc.types.Field(Int, graphql_name='defaultPaymentExpirationYear')
    default_payment_method_id = sgqlc.types.Field(String, graphql_name='defaultPaymentMethodId')
    default_payment_method_last4_digits = sgqlc.types.Field(String, graphql_name='defaultPaymentMethodLast4Digits')
    default_payment_method_type = sgqlc.types.Field(PaymentMethodType, graphql_name='defaultPaymentMethodType')
    email = sgqlc.types.Field(String, graphql_name='email')
    name = sgqlc.types.Field(String, graphql_name='name')


class CustomerPortalColorsPalette(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('background_color', 'border_color', 'current_plan_background', 'icons_color', 'paywall_background_color', 'primary', 'text_color')
    background_color = sgqlc.types.Field(String, graphql_name='backgroundColor')
    border_color = sgqlc.types.Field(String, graphql_name='borderColor')
    current_plan_background = sgqlc.types.Field(String, graphql_name='currentPlanBackground')
    icons_color = sgqlc.types.Field(String, graphql_name='iconsColor')
    paywall_background_color = sgqlc.types.Field(String, graphql_name='paywallBackgroundColor')
    primary = sgqlc.types.Field(String, graphql_name='primary')
    text_color = sgqlc.types.Field(String, graphql_name='textColor')


class CustomerPortalConfiguration(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('custom_css', 'palette', 'typography')
    custom_css = sgqlc.types.Field(String, graphql_name='customCss')
    palette = sgqlc.types.Field(CustomerPortalColorsPalette, graphql_name='palette')
    typography = sgqlc.types.Field('TypographyConfiguration', graphql_name='typography')


class CustomerPortalPricingFeature(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('description', 'display_name', 'feature_type', 'feature_units', 'feature_units_plural', 'id', 'meter_type', 'ref_id')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    feature_type = sgqlc.types.Field(sgqlc.types.non_null(FeatureType), graphql_name='featureType')
    feature_units = sgqlc.types.Field(String, graphql_name='featureUnits')
    feature_units_plural = sgqlc.types.Field(String, graphql_name='featureUnitsPlural')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    meter_type = sgqlc.types.Field(MeterType, graphql_name='meterType')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class CustomerPortalPromotionalEntitlement(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('description', 'display_name', 'end_date', 'has_unlimited_usage', 'period', 'start_date', 'usage_limit')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    period = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlementPeriod), graphql_name='period')
    start_date = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='startDate')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class CustomerPortalSubscription(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('addons', 'billing_period_range', 'plan_name', 'prices', 'pricing', 'pricing_type', 'scheduled_updates', 'status', 'subscription_id', 'total_price', 'trial_remaining_days')
    addons = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CustomerPortalAddon))), graphql_name='addons')
    billing_period_range = sgqlc.types.Field('DateRange', graphql_name='billingPeriodRange')
    plan_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planName')
    prices = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CustomerPortalSubscriptionPrice'))), graphql_name='prices')
    pricing = sgqlc.types.Field(sgqlc.types.non_null('CustomerPortalSubscriptionPricing'), graphql_name='pricing')
    pricing_type = sgqlc.types.Field(sgqlc.types.non_null(PricingType), graphql_name='pricingType')
    scheduled_updates = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionScheduledUpdate')), graphql_name='scheduledUpdates')
    status = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionStatus), graphql_name='status')
    subscription_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subscriptionId')
    total_price = sgqlc.types.Field('CustomerSubscriptionTotalPrice', graphql_name='totalPrice')
    trial_remaining_days = sgqlc.types.Field(Int, graphql_name='trialRemainingDays')


class CustomerPortalSubscriptionPrice(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_model', 'billing_period', 'feature', 'price')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    feature = sgqlc.types.Field(CustomerPortalPricingFeature, graphql_name='feature')
    price = sgqlc.types.Field('Money', graphql_name='price')


class CustomerPortalSubscriptionPricing(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_country_code', 'billing_model', 'billing_period', 'feature', 'price', 'pricing_type', 'unit_quantity', 'usage_based_estimated_bill')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    feature = sgqlc.types.Field(CustomerPortalPricingFeature, graphql_name='feature')
    price = sgqlc.types.Field('Money', graphql_name='price')
    pricing_type = sgqlc.types.Field(sgqlc.types.non_null(PricingType), graphql_name='pricingType')
    unit_quantity = sgqlc.types.Field(Int, graphql_name='unitQuantity')
    usage_based_estimated_bill = sgqlc.types.Field(Float, graphql_name='usageBasedEstimatedBill')


class CustomerResource(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'customer', 'environment_id', 'resource_id', 'subscriptions')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdAt')
    customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='customer')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    resource_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='resourceId')
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscription'))), graphql_name='subscriptions', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(CustomerSubscriptionFilter, graphql_name='filter', default={'status': {'in': ['ACTIVE', 'IN_TRIAL']}})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(CustomerSubscriptionSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )


class CustomerResourceAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'resource_id')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class CustomerResourceConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CustomerResourceEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class CustomerResourceCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'resource_id')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    resource_id = sgqlc.types.Field(Int, graphql_name='resourceId')


class CustomerResourceEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(CustomerResource), graphql_name='node')


class CustomerResourceMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'resource_id')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class CustomerResourceMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'resource_id')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class CustomerStatistics(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('active_subscriptions_by_pricing_type',)
    active_subscriptions_by_pricing_type = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionPricingTypeStatistics'))), graphql_name='activeSubscriptionsByPricingType')


class CustomerSubscription(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'addons', 'billing_id', 'billing_link_url', 'billing_sync_error', 'cancel_reason', 'cancellation_date', 'coupon', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'customer', 'effective_end_date', 'end_date', 'environment', 'environment_id', 'experiment', 'experiment_info', 'future_updates', 'id', 'is_custom_price_subscription', 'latest_invoice', 'old_billing_id', 'outdated_price_packages', 'payment_collection', 'plan', 'prices', 'pricing_type', 'ref_id', 'resource', 'resource_id', 'scheduled_updates', 'start_date', 'status', 'subscription_entitlements', 'subscription_id', 'sync_states', 'total_price', 'trial_end_date', 'was_in_trial')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionAddon')), graphql_name='addons', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(SubscriptionAddonFilter, graphql_name='filter', default={})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionAddonSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_link_url = sgqlc.types.Field(String, graphql_name='billingLinkUrl')
    billing_sync_error = sgqlc.types.Field(String, graphql_name='billingSyncError')
    cancel_reason = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field(DateTime, graphql_name='cancellationDate')
    coupon = sgqlc.types.Field('SubscriptionCoupon', graphql_name='coupon')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(String, graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field(DateTime, graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field(DateTime, graphql_name='currentBillingPeriodStart')
    customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='customer')
    effective_end_date = sgqlc.types.Field(DateTime, graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment = sgqlc.types.Field(sgqlc.types.non_null('Environment'), graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    experiment = sgqlc.types.Field('Experiment', graphql_name='experiment')
    experiment_info = sgqlc.types.Field('experimentInfo', graphql_name='experimentInfo')
    future_updates = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionFutureUpdate'))), graphql_name='futureUpdates')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_custom_price_subscription = sgqlc.types.Field(Boolean, graphql_name='isCustomPriceSubscription')
    latest_invoice = sgqlc.types.Field('SubscriptionInvoice', graphql_name='latestInvoice')
    old_billing_id = sgqlc.types.Field(String, graphql_name='oldBillingId')
    outdated_price_packages = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='outdatedPricePackages')
    payment_collection = sgqlc.types.Field(sgqlc.types.non_null(PaymentCollection), graphql_name='paymentCollection')
    plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='plan')
    prices = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionPrice')), graphql_name='prices', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(SubscriptionPriceFilter, graphql_name='filter', default={})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionPriceSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    pricing_type = sgqlc.types.Field(sgqlc.types.non_null(PricingType), graphql_name='pricingType')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    resource = sgqlc.types.Field(CustomerResource, graphql_name='resource')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    scheduled_updates = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionScheduledUpdate')), graphql_name='scheduledUpdates')
    start_date = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='startDate')
    status = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionStatus), graphql_name='status')
    subscription_entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlement')), graphql_name='subscriptionEntitlements', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(SubscriptionEntitlementFilter, graphql_name='filter', default={})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionEntitlementSort)), graphql_name='sorting', default=[])),
))
    )
    subscription_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subscriptionId')
    sync_states = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SyncState')), graphql_name='syncStates')
    total_price = sgqlc.types.Field('CustomerSubscriptionTotalPrice', graphql_name='totalPrice')
    trial_end_date = sgqlc.types.Field(DateTime, graphql_name='trialEndDate')
    was_in_trial = sgqlc.types.Field(Boolean, graphql_name='wasInTrial')


class CustomerSubscriptionAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'payment_collection', 'pricing_type', 'ref_id', 'resource_id', 'start_date', 'status', 'subscription_id', 'trial_end_date')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    cancel_reason = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field(DateTime, graphql_name='cancellationDate')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(String, graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field(DateTime, graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field(DateTime, graphql_name='currentBillingPeriodStart')
    effective_end_date = sgqlc.types.Field(DateTime, graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    old_billing_id = sgqlc.types.Field(String, graphql_name='oldBillingId')
    payment_collection = sgqlc.types.Field(PaymentCollection, graphql_name='paymentCollection')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    status = sgqlc.types.Field(SubscriptionStatus, graphql_name='status')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field(DateTime, graphql_name='trialEndDate')


class CustomerSubscriptionConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('CustomerSubscriptionEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class CustomerSubscriptionCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'payment_collection', 'pricing_type', 'ref_id', 'resource_id', 'start_date', 'status', 'subscription_id', 'trial_end_date')
    billing_id = sgqlc.types.Field(Int, graphql_name='billingId')
    cancel_reason = sgqlc.types.Field(Int, graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field(Int, graphql_name='cancellationDate')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(Int, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(Int, graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field(Int, graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field(Int, graphql_name='currentBillingPeriodStart')
    effective_end_date = sgqlc.types.Field(Int, graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field(Int, graphql_name='endDate')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    old_billing_id = sgqlc.types.Field(Int, graphql_name='oldBillingId')
    payment_collection = sgqlc.types.Field(Int, graphql_name='paymentCollection')
    pricing_type = sgqlc.types.Field(Int, graphql_name='pricingType')
    ref_id = sgqlc.types.Field(Int, graphql_name='refId')
    resource_id = sgqlc.types.Field(Int, graphql_name='resourceId')
    start_date = sgqlc.types.Field(Int, graphql_name='startDate')
    status = sgqlc.types.Field(Int, graphql_name='status')
    subscription_id = sgqlc.types.Field(Int, graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field(Int, graphql_name='trialEndDate')


class CustomerSubscriptionEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='node')


class CustomerSubscriptionMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'payment_collection', 'pricing_type', 'ref_id', 'resource_id', 'start_date', 'status', 'subscription_id', 'trial_end_date')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    cancel_reason = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field(DateTime, graphql_name='cancellationDate')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(String, graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field(DateTime, graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field(DateTime, graphql_name='currentBillingPeriodStart')
    effective_end_date = sgqlc.types.Field(DateTime, graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    old_billing_id = sgqlc.types.Field(String, graphql_name='oldBillingId')
    payment_collection = sgqlc.types.Field(PaymentCollection, graphql_name='paymentCollection')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    status = sgqlc.types.Field(SubscriptionStatus, graphql_name='status')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field(DateTime, graphql_name='trialEndDate')


class CustomerSubscriptionMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'cancel_reason', 'cancellation_date', 'created_at', 'crm_id', 'crm_link_url', 'current_billing_period_end', 'current_billing_period_start', 'effective_end_date', 'end_date', 'environment_id', 'id', 'old_billing_id', 'payment_collection', 'pricing_type', 'ref_id', 'resource_id', 'start_date', 'status', 'subscription_id', 'trial_end_date')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    cancel_reason = sgqlc.types.Field(SubscriptionCancelReason, graphql_name='cancelReason')
    cancellation_date = sgqlc.types.Field(DateTime, graphql_name='cancellationDate')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(String, graphql_name='crmLinkUrl')
    current_billing_period_end = sgqlc.types.Field(DateTime, graphql_name='currentBillingPeriodEnd')
    current_billing_period_start = sgqlc.types.Field(DateTime, graphql_name='currentBillingPeriodStart')
    effective_end_date = sgqlc.types.Field(DateTime, graphql_name='effectiveEndDate')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    old_billing_id = sgqlc.types.Field(String, graphql_name='oldBillingId')
    payment_collection = sgqlc.types.Field(PaymentCollection, graphql_name='paymentCollection')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    status = sgqlc.types.Field(SubscriptionStatus, graphql_name='status')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    trial_end_date = sgqlc.types.Field(DateTime, graphql_name='trialEndDate')


class CustomerSubscriptionTotalPrice(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('addons_total', 'sub_total', 'total')
    addons_total = sgqlc.types.Field(sgqlc.types.non_null('Money'), graphql_name='addonsTotal')
    sub_total = sgqlc.types.Field(sgqlc.types.non_null('Money'), graphql_name='subTotal')
    total = sgqlc.types.Field(sgqlc.types.non_null('Money'), graphql_name='total')


class DateRange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('end', 'start')
    end = sgqlc.types.Field(DateTime, graphql_name='end')
    start = sgqlc.types.Field(DateTime, graphql_name='start')


class DefaultTrialConfig(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('duration', 'units')
    duration = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='duration')
    units = sgqlc.types.Field(sgqlc.types.non_null(TrialPeriodUnits), graphql_name='units')


class DefaultTrialConfigChange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'change_type')
    after = sgqlc.types.Field(DefaultTrialConfig, graphql_name='after')
    before = sgqlc.types.Field(DefaultTrialConfig, graphql_name='before')
    change_type = sgqlc.types.Field(ChangeType, graphql_name='changeType')


class DowngradeChangeVariables(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('addon_ref_ids', 'billable_features', 'billing_period', 'downgrade_plan_ref_id')
    addon_ref_ids = sgqlc.types.Field(String, graphql_name='addonRefIds')
    billable_features = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(BillableFeature)), graphql_name='billableFeatures')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    downgrade_plan_ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='downgradePlanRefId')


class DumpEnvironmentForMergeComparison(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('post_merge_dump', 'pre_merge_dump')
    post_merge_dump = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='postMergeDump')
    pre_merge_dump = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='preMergeDump')


class DuplicatedEntityNotAllowedError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'entity_name', 'identifier', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    entity_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='entityName')
    identifier = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='identifier')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class EditAllowedOnDraftPackageOnlyError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class EligibleForTrial(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('eligible', 'product_id', 'product_ref_id')
    eligible = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='eligible')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    product_ref_id = sgqlc.types.Field(String, graphql_name='productRefId')


class Entitlement(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('access_denied_reason', 'current_usage', 'customer_id', 'display_name_override', 'entitlement_updated_at', 'feature', 'has_soft_limit', 'has_unlimited_usage', 'hidden_from_widgets', 'is_granted', 'meter_id', 'next_reset_date', 'requested_usage', 'reset_period', 'reset_period_configuration', 'resource_id', 'usage_limit', 'usage_updated_at')
    access_denied_reason = sgqlc.types.Field(AccessDeniedReason, graphql_name='accessDeniedReason')
    current_usage = sgqlc.types.Field(Float, graphql_name='currentUsage')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    display_name_override = sgqlc.types.Field(String, graphql_name='displayNameOverride')
    entitlement_updated_at = sgqlc.types.Field(DateTime, graphql_name='entitlementUpdatedAt')
    feature = sgqlc.types.Field('EntitlementFeature', graphql_name='feature')
    has_soft_limit = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasSoftLimit')
    has_unlimited_usage = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasUnlimitedUsage')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    is_granted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isGranted')
    meter_id = sgqlc.types.Field(String, graphql_name='meterId')
    next_reset_date = sgqlc.types.Field(DateTime, graphql_name='nextResetDate')
    requested_usage = sgqlc.types.Field(Float, graphql_name='requestedUsage')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    reset_period_configuration = sgqlc.types.Field('ResetPeriodConfiguration', graphql_name='resetPeriodConfiguration')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    usage_updated_at = sgqlc.types.Field(DateTime, graphql_name='usageUpdatedAt')


class EntitlementFeature(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'description', 'display_name', 'feature_status', 'feature_type', 'feature_units', 'feature_units_plural', 'id', 'meter_type', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    feature_status = sgqlc.types.Field(sgqlc.types.non_null(FeatureStatus), graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(sgqlc.types.non_null(FeatureType), graphql_name='featureType')
    feature_units = sgqlc.types.Field(String, graphql_name='featureUnits')
    feature_units_plural = sgqlc.types.Field(String, graphql_name='featureUnitsPlural')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    meter_type = sgqlc.types.Field(MeterType, graphql_name='meterType')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class EntitlementLimitExceededError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'feature', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    feature = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='feature')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class EntitlementSummary(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('addon_quantity', 'feature_package_entitlement', 'feature_promotional_entitlement', 'is_effective_entitlement', 'plan', 'price_entitlement', 'subscription')
    addon_quantity = sgqlc.types.Field(Float, graphql_name='addonQuantity')
    feature_package_entitlement = sgqlc.types.Field('PackageEntitlement', graphql_name='featurePackageEntitlement')
    feature_promotional_entitlement = sgqlc.types.Field('PromotionalEntitlement', graphql_name='featurePromotionalEntitlement')
    is_effective_entitlement = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isEffectiveEntitlement')
    plan = sgqlc.types.Field('Plan', graphql_name='plan')
    price_entitlement = sgqlc.types.Field('PriceEntitlement', graphql_name='priceEntitlement')
    subscription = sgqlc.types.Field(CustomerSubscription, graphql_name='subscription')


class EntitlementWithSummary(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('access_denied_reason', 'current_usage', 'customer_id', 'display_name_override', 'entitlement_updated_at', 'feature', 'has_soft_limit', 'has_unlimited_usage', 'hidden_from_widgets', 'is_granted', 'meter_id', 'next_reset_date', 'requested_usage', 'reset_period', 'reset_period_configuration', 'resource_id', 'summaries', 'usage_limit', 'usage_updated_at')
    access_denied_reason = sgqlc.types.Field(AccessDeniedReason, graphql_name='accessDeniedReason')
    current_usage = sgqlc.types.Field(Float, graphql_name='currentUsage')
    customer_id = sgqlc.types.Field(String, graphql_name='customerId')
    display_name_override = sgqlc.types.Field(String, graphql_name='displayNameOverride')
    entitlement_updated_at = sgqlc.types.Field(DateTime, graphql_name='entitlementUpdatedAt')
    feature = sgqlc.types.Field(EntitlementFeature, graphql_name='feature')
    has_soft_limit = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasSoftLimit')
    has_unlimited_usage = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasUnlimitedUsage')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    is_granted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isGranted')
    meter_id = sgqlc.types.Field(String, graphql_name='meterId')
    next_reset_date = sgqlc.types.Field(DateTime, graphql_name='nextResetDate')
    requested_usage = sgqlc.types.Field(Float, graphql_name='requestedUsage')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    reset_period_configuration = sgqlc.types.Field('ResetPeriodConfiguration', graphql_name='resetPeriodConfiguration')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    summaries = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(EntitlementSummary)), graphql_name='summaries')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')
    usage_updated_at = sgqlc.types.Field(DateTime, graphql_name='usageUpdatedAt')


class EntitlementsUpdated(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account_id', 'customer_id', 'entitlements', 'environment_id', 'resource_id')
    account_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='accountId')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Entitlement))), graphql_name='entitlements')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class Environment(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account', 'api_keys', 'color', 'created_at', 'description', 'display_name', 'harden_client_access_enabled', 'id', 'is_sandbox', 'permanent_deletion_date', 'provision_status', 'signing_token', 'slug', 'type')
    account = sgqlc.types.Field(Account, graphql_name='account')
    api_keys = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ApiKey))), graphql_name='apiKeys', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ApiKeyFilter, graphql_name='filter', default={})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ApiKeySort)), graphql_name='sorting', default=[])),
))
    )
    color = sgqlc.types.Field(String, graphql_name='color')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    harden_client_access_enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hardenClientAccessEnabled')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_sandbox = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isSandbox')
    permanent_deletion_date = sgqlc.types.Field(DateTime, graphql_name='permanentDeletionDate')
    provision_status = sgqlc.types.Field(EnvironmentProvisionStatus, graphql_name='provisionStatus')
    signing_token = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='signingToken')
    slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='slug')
    type = sgqlc.types.Field(sgqlc.types.non_null(EnvironmentType), graphql_name='type')


class EnvironmentAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'display_name', 'id', 'permanent_deletion_date', 'slug')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    id = sgqlc.types.Field(String, graphql_name='id')
    permanent_deletion_date = sgqlc.types.Field(DateTime, graphql_name='permanentDeletionDate')
    slug = sgqlc.types.Field(String, graphql_name='slug')


class EnvironmentConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('EnvironmentEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')


class EnvironmentCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'display_name', 'id', 'permanent_deletion_date', 'slug')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    display_name = sgqlc.types.Field(Int, graphql_name='displayName')
    id = sgqlc.types.Field(Int, graphql_name='id')
    permanent_deletion_date = sgqlc.types.Field(Int, graphql_name='permanentDeletionDate')
    slug = sgqlc.types.Field(Int, graphql_name='slug')


class EnvironmentEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Environment), graphql_name='node')


class EnvironmentMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'display_name', 'id', 'permanent_deletion_date', 'slug')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    id = sgqlc.types.Field(String, graphql_name='id')
    permanent_deletion_date = sgqlc.types.Field(DateTime, graphql_name='permanentDeletionDate')
    slug = sgqlc.types.Field(String, graphql_name='slug')


class EnvironmentMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'display_name', 'id', 'permanent_deletion_date', 'slug')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    id = sgqlc.types.Field(String, graphql_name='id')
    permanent_deletion_date = sgqlc.types.Field(DateTime, graphql_name='permanentDeletionDate')
    slug = sgqlc.types.Field(String, graphql_name='slug')


class EnvironmentMissingError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class EventLog(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('description', 'environment', 'environment_id', 'event_log_type', 'id', 'webhook_endpoints')
    description = sgqlc.types.Field(String, graphql_name='description')
    environment = sgqlc.types.Field(Environment, graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    event_log_type = sgqlc.types.Field(sgqlc.types.non_null(EventLogType), graphql_name='eventLogType')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    webhook_endpoints = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='webhookEndpoints')


class EventLogAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('environment_id', 'id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')


class EventLogCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('environment_id', 'id')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')


class EventLogEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(EventLog), graphql_name='node')


class EventLogMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('environment_id', 'id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')


class EventLogMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('environment_id', 'id')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')


class EventsFields(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('fields',)
    fields = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='fields')


class Experiment(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('control_group_name', 'created_at', 'customers', 'description', 'environment', 'environment_id', 'id', 'initial_product_settings', 'name', 'product', 'product_id', 'product_settings', 'ref_id', 'started_at', 'status', 'stopped_at', 'updated_at', 'variant_group_name', 'variant_percentage')
    control_group_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='controlGroupName')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdAt')
    customers = sgqlc.types.Field(Customer, graphql_name='customers')
    description = sgqlc.types.Field(String, graphql_name='description')
    environment = sgqlc.types.Field(Environment, graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    initial_product_settings = sgqlc.types.Field('ProductSettings', graphql_name='initialProductSettings')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    product = sgqlc.types.Field('Product', graphql_name='product')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='productId')
    product_settings = sgqlc.types.Field(sgqlc.types.non_null('ProductSettings'), graphql_name='productSettings')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    started_at = sgqlc.types.Field(DateTime, graphql_name='startedAt')
    status = sgqlc.types.Field(sgqlc.types.non_null(ExperimentStatus), graphql_name='status')
    stopped_at = sgqlc.types.Field(DateTime, graphql_name='stoppedAt')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')
    variant_group_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='variantGroupName')
    variant_percentage = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='variantPercentage')


class ExperimentAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'name', 'product_id', 'ref_id', 'status')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(ExperimentStatus, graphql_name='status')


class ExperimentAvgAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(Float, graphql_name='id')


class ExperimentConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ExperimentEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class ExperimentCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'name', 'product_id', 'ref_id', 'status')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    name = sgqlc.types.Field(Int, graphql_name='name')
    product_id = sgqlc.types.Field(Int, graphql_name='productId')
    ref_id = sgqlc.types.Field(Int, graphql_name='refId')
    status = sgqlc.types.Field(Int, graphql_name='status')


class ExperimentEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Experiment), graphql_name='node')


class ExperimentMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'name', 'product_id', 'ref_id', 'status')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(ExperimentStatus, graphql_name='status')


class ExperimentMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'name', 'product_id', 'ref_id', 'status')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    name = sgqlc.types.Field(String, graphql_name='name')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(ExperimentStatus, graphql_name='status')


class ExperimentStats(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('control_paid_subscriptions', 'control_subscriptions', 'variant_paid_subscriptions', 'variant_subscriptions')
    control_paid_subscriptions = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='controlPaidSubscriptions')
    control_subscriptions = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='controlSubscriptions')
    variant_paid_subscriptions = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='variantPaidSubscriptions')
    variant_subscriptions = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='variantSubscriptions')


class ExperimentSumAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(Float, graphql_name='id')


class FailedToImportCustomerError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'code', 'is_validation_error')
    billing_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='billingId')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class Feature(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account', 'additional_meta_data', 'created_at', 'description', 'display_name', 'environment', 'environment_id', 'feature_status', 'feature_type', 'feature_units', 'feature_units_plural', 'has_entitlements', 'has_meter', 'id', 'meter', 'meter_type', 'ref_id', 'updated_at')
    account = sgqlc.types.Field(Account, graphql_name='account')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    environment = sgqlc.types.Field(Environment, graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature_status = sgqlc.types.Field(sgqlc.types.non_null(FeatureStatus), graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(sgqlc.types.non_null(FeatureType), graphql_name='featureType')
    feature_units = sgqlc.types.Field(String, graphql_name='featureUnits')
    feature_units_plural = sgqlc.types.Field(String, graphql_name='featureUnitsPlural')
    has_entitlements = sgqlc.types.Field(Boolean, graphql_name='hasEntitlements')
    has_meter = sgqlc.types.Field(Boolean, graphql_name='hasMeter')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    meter = sgqlc.types.Field('Meter', graphql_name='meter')
    meter_type = sgqlc.types.Field(MeterType, graphql_name='meterType')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')


class FeatureAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'id', 'meter_type', 'ref_id', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_status = sgqlc.types.Field(FeatureStatus, graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(FeatureType, graphql_name='featureType')
    id = sgqlc.types.Field(String, graphql_name='id')
    meter_type = sgqlc.types.Field(MeterType, graphql_name='meterType')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class FeatureConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('FeatureEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class FeatureCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'id', 'meter_type', 'ref_id', 'updated_at')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    description = sgqlc.types.Field(Int, graphql_name='description')
    display_name = sgqlc.types.Field(Int, graphql_name='displayName')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    feature_status = sgqlc.types.Field(Int, graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(Int, graphql_name='featureType')
    id = sgqlc.types.Field(Int, graphql_name='id')
    meter_type = sgqlc.types.Field(Int, graphql_name='meterType')
    ref_id = sgqlc.types.Field(Int, graphql_name='refId')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')


class FeatureEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='node')


class FeatureMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'id', 'meter_type', 'ref_id', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_status = sgqlc.types.Field(FeatureStatus, graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(FeatureType, graphql_name='featureType')
    id = sgqlc.types.Field(String, graphql_name='id')
    meter_type = sgqlc.types.Field(MeterType, graphql_name='meterType')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class FeatureMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'display_name', 'environment_id', 'feature_status', 'feature_type', 'id', 'meter_type', 'ref_id', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_status = sgqlc.types.Field(FeatureStatus, graphql_name='featureStatus')
    feature_type = sgqlc.types.Field(FeatureType, graphql_name='featureType')
    id = sgqlc.types.Field(String, graphql_name='id')
    meter_type = sgqlc.types.Field(MeterType, graphql_name='meterType')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class FeatureNotFoundError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class FontVariant(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('font_size', 'font_weight')
    font_size = sgqlc.types.Field(Float, graphql_name='fontSize')
    font_weight = sgqlc.types.Field(FontWeight, graphql_name='fontWeight')


class GetAwsExternalIdResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('external_id',)
    external_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='externalId')


class HiddenFromWidgetsChange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'change_type')
    after = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='after')
    before = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='before')
    change_type = sgqlc.types.Field(ChangeType, graphql_name='changeType')


class Hook(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account', 'created_at', 'description', 'endpoint', 'environment', 'environment_id', 'event_log_types', 'id', 'secret_key', 'status')
    account = sgqlc.types.Field(Account, graphql_name='account')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    endpoint = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='endpoint')
    environment = sgqlc.types.Field(Environment, graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    event_log_types = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(EventLogType))), graphql_name='eventLogTypes')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    secret_key = sgqlc.types.Field(String, graphql_name='secretKey')
    status = sgqlc.types.Field(sgqlc.types.non_null(HookStatus), graphql_name='status')


class HookAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'endpoint', 'environment_id', 'id', 'status')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    endpoint = sgqlc.types.Field(String, graphql_name='endpoint')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(HookStatus, graphql_name='status')


class HookConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('HookEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class HookCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'endpoint', 'environment_id', 'id', 'status')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    endpoint = sgqlc.types.Field(Int, graphql_name='endpoint')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    status = sgqlc.types.Field(Int, graphql_name='status')


class HookDeleteResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'endpoint', 'environment_id', 'event_log_types', 'id', 'secret_key', 'status')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    endpoint = sgqlc.types.Field(String, graphql_name='endpoint')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    event_log_types = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(EventLogType)), graphql_name='eventLogTypes')
    id = sgqlc.types.Field(String, graphql_name='id')
    secret_key = sgqlc.types.Field(String, graphql_name='secretKey')
    status = sgqlc.types.Field(HookStatus, graphql_name='status')


class HookEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Hook), graphql_name='node')


class HookMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'endpoint', 'environment_id', 'id', 'status')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    endpoint = sgqlc.types.Field(String, graphql_name='endpoint')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(HookStatus, graphql_name='status')


class HookMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'endpoint', 'environment_id', 'id', 'status')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    endpoint = sgqlc.types.Field(String, graphql_name='endpoint')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(HookStatus, graphql_name='status')


class HubspotCredentials(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('hub_domain',)
    hub_domain = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='hubDomain')


class IdentityForbiddenError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('accessed_field', 'code', 'current_identity_type', 'is_validation_error', 'required_identity_type')
    accessed_field = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='accessedField')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    current_identity_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='currentIdentityType')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    required_identity_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='requiredIdentityType')


class ImmediateSubscriptionPreviewInvoice(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('credits', 'discount', 'discount_details', 'proration', 'sub_total', 'tax', 'tax_details', 'total', 'total_excluding_tax')
    credits = sgqlc.types.Field('SubscriptionPreviewCredits', graphql_name='credits')
    discount = sgqlc.types.Field('Money', graphql_name='discount')
    discount_details = sgqlc.types.Field('SubscriptionPreviewDiscount', graphql_name='discountDetails')
    proration = sgqlc.types.Field('SubscriptionPreviewProrations', graphql_name='proration')
    sub_total = sgqlc.types.Field(sgqlc.types.non_null('Money'), graphql_name='subTotal')
    tax = sgqlc.types.Field('Money', graphql_name='tax')
    tax_details = sgqlc.types.Field('SubscriptionPreviewTaxDetails', graphql_name='taxDetails')
    total = sgqlc.types.Field(sgqlc.types.non_null('Money'), graphql_name='total')
    total_excluding_tax = sgqlc.types.Field(sgqlc.types.non_null('Money'), graphql_name='totalExcludingTax')


class ImportAlreadyInProgressError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class ImportIntegrationTask(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'customers_count', 'end_date', 'environment_id', 'id', 'import_errors', 'products_count', 'progress', 'start_date', 'status', 'task_type', 'total_subtasks_count')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    customers_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='customersCount')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    import_errors = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ImportSubTaskError'))), graphql_name='importErrors')
    products_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='productsCount')
    progress = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='progress')
    start_date = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='startDate')
    status = sgqlc.types.Field(sgqlc.types.non_null(TaskStatus), graphql_name='status')
    task_type = sgqlc.types.Field(sgqlc.types.non_null(TaskType), graphql_name='taskType')
    total_subtasks_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalSubtasksCount')


class ImportIntegrationTaskAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'task_type')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(TaskStatus, graphql_name='status')
    task_type = sgqlc.types.Field(TaskType, graphql_name='taskType')


class ImportIntegrationTaskConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ImportIntegrationTaskEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')


class ImportIntegrationTaskCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'task_type')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    status = sgqlc.types.Field(Int, graphql_name='status')
    task_type = sgqlc.types.Field(Int, graphql_name='taskType')


class ImportIntegrationTaskEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(ImportIntegrationTask), graphql_name='node')


class ImportIntegrationTaskMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'task_type')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(TaskStatus, graphql_name='status')
    task_type = sgqlc.types.Field(TaskType, graphql_name='taskType')


class ImportIntegrationTaskMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'task_type')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(TaskStatus, graphql_name='status')
    task_type = sgqlc.types.Field(TaskType, graphql_name='taskType')


class ImportSubTaskError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('error', 'id')
    error = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='error')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class InitAddStripeCustomerPaymentMethod(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('payment_intent_client_secret',)
    payment_intent_client_secret = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='paymentIntentClientSecret')


class InitStripePaymentMethodError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class Integration(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account', 'created_at', 'credentials', 'environment', 'environment_id', 'id', 'vendor_identifier')
    account = sgqlc.types.Field(Account, graphql_name='account')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    credentials = sgqlc.types.Field('Credentials', graphql_name='credentials')
    environment = sgqlc.types.Field(Environment, graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    vendor_identifier = sgqlc.types.Field(sgqlc.types.non_null(VendorIdentifier), graphql_name='vendorIdentifier')


class IntegrationAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'vendor_identifier')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    vendor_identifier = sgqlc.types.Field(VendorIdentifier, graphql_name='vendorIdentifier')


class IntegrationConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('IntegrationEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class IntegrationCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'vendor_identifier')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    vendor_identifier = sgqlc.types.Field(Int, graphql_name='vendorIdentifier')


class IntegrationDeleteResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'credentials', 'environment_id', 'id', 'vendor_identifier')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    credentials = sgqlc.types.Field('Credentials', graphql_name='credentials')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    vendor_identifier = sgqlc.types.Field(VendorIdentifier, graphql_name='vendorIdentifier')


class IntegrationEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Integration), graphql_name='node')


class IntegrationMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'vendor_identifier')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    vendor_identifier = sgqlc.types.Field(VendorIdentifier, graphql_name='vendorIdentifier')


class IntegrationMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'vendor_identifier')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    vendor_identifier = sgqlc.types.Field(VendorIdentifier, graphql_name='vendorIdentifier')


class InvalidArgumentError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class InvalidCancellationDate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class InvalidEntitlementResetPeriodError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class InvalidMemberDeleteError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class InvalidSubscriptionStatus(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class InvoiceLine(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('amount', 'currency', 'description', 'proration', 'quantity')
    amount = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='amount')
    currency = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='currency')
    description = sgqlc.types.Field(String, graphql_name='description')
    proration = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='proration')
    quantity = sgqlc.types.Field(Int, graphql_name='quantity')


class ListAwsProductDimensionsDTO(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('dimensions',)
    dimensions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AwsDimension))), graphql_name='dimensions')


class ListAwsProductsResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('products',)
    products = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AwsProduct))), graphql_name='products')


class Member(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account', 'created_at', 'cubejs_token', 'customer_token', 'email', 'hide_getting_started_page', 'id', 'member_status', 'service_api_key', 'user')
    account = sgqlc.types.Field(sgqlc.types.non_null(Account), graphql_name='account')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    cubejs_token = sgqlc.types.Field(String, graphql_name='cubejsToken')
    customer_token = sgqlc.types.Field(String, graphql_name='customerToken')
    email = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='email')
    hide_getting_started_page = sgqlc.types.Field(Boolean, graphql_name='hideGettingStartedPage')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    member_status = sgqlc.types.Field(sgqlc.types.non_null(MemberStatus), graphql_name='memberStatus')
    service_api_key = sgqlc.types.Field(String, graphql_name='serviceApiKey')
    user = sgqlc.types.Field('User', graphql_name='user')


class MemberAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'id')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(String, graphql_name='id')


class MemberConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MemberEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class MemberCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'id')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    id = sgqlc.types.Field(Int, graphql_name='id')


class MemberEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Member), graphql_name='node')


class MemberInvitationError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'reason')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    reason = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='reason')


class MemberMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'id')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(String, graphql_name='id')


class MemberMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'id')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(String, graphql_name='id')


class MemberNotFoundError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code',)
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')


class MembersInviteResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('failed_invites', 'skipped_invites', 'success_invites')
    failed_invites = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='failedInvites')
    skipped_invites = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='skippedInvites')
    success_invites = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='successInvites')


class MergeEnvironment(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('environment_slug', 'task_ids')
    environment_slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentSlug')
    task_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='taskIds')


class Meter(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('aggregation', 'created_at', 'environment_id', 'filters', 'id', 'updated_at')
    aggregation = sgqlc.types.Field(sgqlc.types.non_null(Aggregation), graphql_name='aggregation')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdAt')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    filters = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('MeterFilterDefinition'))), graphql_name='filters')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')


class MeterCondition(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('field', 'operation', 'value')
    field = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='field')
    operation = sgqlc.types.Field(sgqlc.types.non_null(ConditionOperation), graphql_name='operation')
    value = sgqlc.types.Field(String, graphql_name='value')


class MeterFilterDefinition(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('conditions',)
    conditions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MeterCondition))), graphql_name='conditions')


class MeteringNotAvailableForFeatureTypeError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'feature_type', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    feature_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureType')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class MockPaywall(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('configuration', 'plans')
    configuration = sgqlc.types.Field('PaywallConfiguration', graphql_name='configuration')
    plans = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PaywallPlan'))), graphql_name='plans')


class Money(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('amount', 'currency')
    amount = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='amount')
    currency = sgqlc.types.Field(sgqlc.types.non_null(Currency), graphql_name='currency')


class MonthlyResetPeriodConfig(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('monthly_according_to',)
    monthly_according_to = sgqlc.types.Field(MonthlyAccordingTo, graphql_name='monthlyAccordingTo')


class Mutation(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('add_compatible_addons_to_plan', 'apply_subscription', 'archive_customer', 'archive_environment', 'archive_feature', 'archive_one_coupon', 'archive_plan', 'attach_customer_payment_method', 'cancel_schedule', 'cancel_subscription', 'create_account', 'create_addon_draft', 'create_empty_addon_draft', 'create_empty_plan_draft', 'create_feature', 'create_many_package_entitlements', 'create_many_promotional_entitlements', 'create_one_addon', 'create_one_coupon', 'create_one_customer', 'create_one_environment', 'create_one_experiment', 'create_one_feature', 'create_one_hook', 'create_one_integration', 'create_one_plan', 'create_one_product', 'create_or_update_aws_marketplace_product', 'create_plan_draft', 'create_subscription', 'create_usage_measurement', 'delete_feature', 'delete_one_addon', 'delete_one_feature', 'delete_one_hook', 'delete_one_integration', 'delete_one_package_entitlement', 'delete_one_price', 'delete_one_product', 'delete_one_promotional_entitlement', 'detach_customer_payment_method', 'duplicate_product', 'estimate_subscription', 'estimate_subscription_update', 'grant_promotional_entitlements', 'hide_getting_started_page', 'import_customers_bulk', 'import_one_customer', 'import_subscriptions_bulk', 'init_add_stripe_customer_payment_method', 'invite_members', 'merge_environment', 'migrate_subscription_to_latest', 'preview_subscription', 'provision_customer', 'provision_sandbox', 'provision_subscription', 'provision_subscription_v2', 'publish_addon', 'publish_plan', 'purge_customer_cache', 'recalculate_entitlements', 'register_member', 'remove_addon_draft', 'remove_base_plan_from_plan', 'remove_compatible_addons_from_plan', 'remove_coupon_from_customer', 'remove_coupon_from_customer_subscription', 'remove_experiment_from_customer', 'remove_experiment_from_customer_subscription', 'remove_member', 'remove_plan_draft', 'report_entitlement_check_requested', 'report_event', 'report_usage', 'report_usage_bulk', 'resend_email_verification', 'resync_integration', 'revoke_promotional_entitlement', 'set_base_plan_on_plan', 'set_compatible_addons_on_plan', 'set_coupon_on_customer', 'set_coupon_on_customer_subscription', 'set_experiment_on_customer', 'set_experiment_on_customer_subscription', 'set_package_pricing', 'set_widget_configuration', 'start_experiment', 'stop_experiment', 'sync_tax_rates', 'transfer_subscription', 'trigger_import_catalog', 'trigger_import_customers', 'trigger_plan_subscription_migration', 'unarchive_customer', 'unarchive_environment', 'update_account', 'update_entitlements_order', 'update_feature', 'update_one_addon', 'update_one_coupon', 'update_one_customer', 'update_one_environment', 'update_one_experiment', 'update_one_feature', 'update_one_hook', 'update_one_integration', 'update_one_package_entitlement', 'update_one_plan', 'update_one_product', 'update_one_promotional_entitlement', 'update_one_subscription', 'update_user')
    add_compatible_addons_to_plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='addCompatibleAddonsToPlan', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddCompatibleAddonsToPlanInput), graphql_name='input', default=None)),
))
    )
    apply_subscription = sgqlc.types.Field(sgqlc.types.non_null(ApplySubscription), graphql_name='applySubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ApplySubscriptionInput), graphql_name='input', default=None)),
))
    )
    archive_customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='archiveCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ArchiveCustomerInput), graphql_name='input', default=None)),
))
    )
    archive_environment = sgqlc.types.Field(sgqlc.types.non_null(Environment), graphql_name='archiveEnvironment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ArchiveEnvironmentInput), graphql_name='input', default=None)),
))
    )
    archive_feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='archiveFeature', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ArchiveFeatureInput), graphql_name='input', default=None)),
))
    )
    archive_one_coupon = sgqlc.types.Field(sgqlc.types.non_null(Coupon), graphql_name='archiveOneCoupon', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ArchiveCouponInput), graphql_name='input', default=None)),
))
    )
    archive_plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='archivePlan', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ArchivePlanInput), graphql_name='input', default=None)),
))
    )
    attach_customer_payment_method = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='attachCustomerPaymentMethod', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AttachCustomerPaymentMethodInput), graphql_name='input', default=None)),
))
    )
    cancel_schedule = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='cancelSchedule', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SubscriptionUpdateScheduleCancellationInput), graphql_name='input', default=None)),
))
    )
    cancel_subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='cancelSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SubscriptionCancellationInput), graphql_name='input', default=None)),
))
    )
    create_account = sgqlc.types.Field(sgqlc.types.non_null(Member), graphql_name='createAccount', args=sgqlc.types.ArgDict((
        ('account_name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='accountName', default=None)),
))
    )
    create_addon_draft = sgqlc.types.Field(sgqlc.types.non_null(Addon), graphql_name='createAddonDraft', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='id', default=None)),
))
    )
    create_empty_addon_draft = sgqlc.types.Field(sgqlc.types.non_null(Addon), graphql_name='createEmptyAddonDraft', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='id', default=None)),
))
    )
    create_empty_plan_draft = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='createEmptyPlanDraft', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='id', default=None)),
))
    )
    create_feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='createFeature', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(FeatureInput), graphql_name='input', default=None)),
))
    )
    create_many_package_entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlement'))), graphql_name='createManyPackageEntitlements', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateManyPackageEntitlementsInput), graphql_name='input', default=None)),
))
    )
    create_many_promotional_entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PromotionalEntitlement'))), graphql_name='createManyPromotionalEntitlements', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateManyPromotionalEntitlementsInput), graphql_name='input', default=None)),
))
    )
    create_one_addon = sgqlc.types.Field(sgqlc.types.non_null(Addon), graphql_name='createOneAddon', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddonCreateInput), graphql_name='input', default=None)),
))
    )
    create_one_coupon = sgqlc.types.Field(sgqlc.types.non_null(Coupon), graphql_name='createOneCoupon', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateCouponInput), graphql_name='input', default=None)),
))
    )
    create_one_customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='createOneCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CustomerInput), graphql_name='input', default=None)),
))
    )
    create_one_environment = sgqlc.types.Field(sgqlc.types.non_null(Environment), graphql_name='createOneEnvironment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateOneEnvironmentInput), graphql_name='input', default=None)),
))
    )
    create_one_experiment = sgqlc.types.Field(sgqlc.types.non_null(Experiment), graphql_name='createOneExperiment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateExperimentInput), graphql_name='input', default=None)),
))
    )
    create_one_feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='createOneFeature', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateOneFeatureInput), graphql_name='input', default=None)),
))
    )
    create_one_hook = sgqlc.types.Field(sgqlc.types.non_null(Hook), graphql_name='createOneHook', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateOneHookInput), graphql_name='input', default=None)),
))
    )
    create_one_integration = sgqlc.types.Field(sgqlc.types.non_null(Integration), graphql_name='createOneIntegration', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateOneIntegrationInput), graphql_name='input', default=None)),
))
    )
    create_one_plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='createOnePlan', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PlanCreateInput), graphql_name='input', default=None)),
))
    )
    create_one_product = sgqlc.types.Field(sgqlc.types.non_null('Product'), graphql_name='createOneProduct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateOneProductInput), graphql_name='input', default=None)),
))
    )
    create_or_update_aws_marketplace_product = sgqlc.types.Field(sgqlc.types.non_null('Product'), graphql_name='createOrUpdateAwsMarketplaceProduct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateOrUpdateAwsMarketplaceProductInput), graphql_name='input', default=None)),
))
    )
    create_plan_draft = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='createPlanDraft', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='id', default=None)),
))
    )
    create_subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='createSubscription', args=sgqlc.types.ArgDict((
        ('subscription', sgqlc.types.Arg(sgqlc.types.non_null(SubscriptionInput), graphql_name='subscription', default=None)),
))
    )
    create_usage_measurement = sgqlc.types.Field(sgqlc.types.non_null('UsageMeasurementWithCurrentUsage'), graphql_name='createUsageMeasurement', args=sgqlc.types.ArgDict((
        ('usage_measurement', sgqlc.types.Arg(sgqlc.types.non_null(UsageMeasurementCreateInput), graphql_name='usageMeasurement', default=None)),
))
    )
    delete_feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='deleteFeature', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteFeatureInput), graphql_name='input', default=None)),
))
    )
    delete_one_addon = sgqlc.types.Field(sgqlc.types.non_null(AddonDeleteResponse), graphql_name='deleteOneAddon', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteOneAddonInput), graphql_name='input', default=None)),
))
    )
    delete_one_feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='deleteOneFeature', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteFeatureInput), graphql_name='input', default=None)),
))
    )
    delete_one_hook = sgqlc.types.Field(sgqlc.types.non_null(HookDeleteResponse), graphql_name='deleteOneHook', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteOneHookInput), graphql_name='input', default=None)),
))
    )
    delete_one_integration = sgqlc.types.Field(sgqlc.types.non_null(IntegrationDeleteResponse), graphql_name='deleteOneIntegration', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteOneIntegrationInput), graphql_name='input', default=None)),
))
    )
    delete_one_package_entitlement = sgqlc.types.Field(sgqlc.types.non_null('PackageEntitlementDeleteResponse'), graphql_name='deleteOnePackageEntitlement', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteOnePackageEntitlementInput), graphql_name='input', default=None)),
))
    )
    delete_one_price = sgqlc.types.Field(sgqlc.types.non_null('PriceDeleteResponse'), graphql_name='deleteOnePrice', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteOnePriceInput), graphql_name='input', default=None)),
))
    )
    delete_one_product = sgqlc.types.Field(sgqlc.types.non_null('ProductDeleteResponse'), graphql_name='deleteOneProduct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteOneProductInput), graphql_name='input', default=None)),
))
    )
    delete_one_promotional_entitlement = sgqlc.types.Field(sgqlc.types.non_null('PromotionalEntitlementDeleteResponse'), graphql_name='deleteOnePromotionalEntitlement', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteOnePromotionalEntitlementInput), graphql_name='input', default=None)),
))
    )
    detach_customer_payment_method = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='detachCustomerPaymentMethod', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DetachCustomerPaymentMethodInput), graphql_name='input', default=None)),
))
    )
    duplicate_product = sgqlc.types.Field(sgqlc.types.non_null('Product'), graphql_name='duplicateProduct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DuplicateProductInput), graphql_name='input', default=None)),
))
    )
    estimate_subscription = sgqlc.types.Field(sgqlc.types.non_null('SubscriptionPreview'), graphql_name='estimateSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(EstimateSubscriptionInput), graphql_name='input', default=None)),
))
    )
    estimate_subscription_update = sgqlc.types.Field(sgqlc.types.non_null('SubscriptionPreview'), graphql_name='estimateSubscriptionUpdate', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(EstimateSubscriptionUpdateInput), graphql_name='input', default=None)),
))
    )
    grant_promotional_entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PromotionalEntitlement'))), graphql_name='grantPromotionalEntitlements', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(GrantPromotionalEntitlementsInput), graphql_name='input', default=None)),
))
    )
    hide_getting_started_page = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='hideGettingStartedPage', args=sgqlc.types.ArgDict((
        ('member_id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='memberId', default=None)),
))
    )
    import_customers_bulk = sgqlc.types.Field(String, graphql_name='importCustomersBulk', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ImportCustomerBulk), graphql_name='input', default=None)),
))
    )
    import_one_customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='importOneCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ImportCustomerInput), graphql_name='input', default=None)),
))
    )
    import_subscriptions_bulk = sgqlc.types.Field(String, graphql_name='importSubscriptionsBulk', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ImportSubscriptionsBulk), graphql_name='input', default=None)),
))
    )
    init_add_stripe_customer_payment_method = sgqlc.types.Field(sgqlc.types.non_null(InitAddStripeCustomerPaymentMethod), graphql_name='initAddStripeCustomerPaymentMethod', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(InitAddStripeCustomerPaymentMethodInput), graphql_name='input', default=None)),
))
    )
    invite_members = sgqlc.types.Field(sgqlc.types.non_null(MembersInviteResponse), graphql_name='inviteMembers', args=sgqlc.types.ArgDict((
        ('invites', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='invites', default=None)),
))
    )
    merge_environment = sgqlc.types.Field(sgqlc.types.non_null(MergeEnvironment), graphql_name='mergeEnvironment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(MergeEnvironmentInput), graphql_name='input', default=None)),
))
    )
    migrate_subscription_to_latest = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='migrateSubscriptionToLatest', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SubscriptionMigrationInput), graphql_name='input', default=None)),
))
    )
    preview_subscription = sgqlc.types.Field(sgqlc.types.non_null('SubscriptionPreviewV2'), graphql_name='previewSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PreviewSubscriptionInput), graphql_name='input', default=None)),
))
    )
    provision_customer = sgqlc.types.Field(sgqlc.types.non_null('ProvisionedCustomer'), graphql_name='provisionCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ProvisionCustomerInput), graphql_name='input', default=None)),
))
    )
    provision_sandbox = sgqlc.types.Field(sgqlc.types.non_null(Environment), graphql_name='provisionSandbox', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ProvisionSandboxInput), graphql_name='input', default=None)),
))
    )
    provision_subscription = sgqlc.types.Field(sgqlc.types.non_null('ProvisionSubscriptionResult'), graphql_name='provisionSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ProvisionSubscription), graphql_name='input', default=None)),
))
    )
    provision_subscription_v2 = sgqlc.types.Field(sgqlc.types.non_null('ProvisionSubscriptionResult'), graphql_name='provisionSubscriptionV2', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ProvisionSubscriptionInput), graphql_name='input', default=None)),
))
    )
    publish_addon = sgqlc.types.Field(sgqlc.types.non_null('PublishPackageResult'), graphql_name='publishAddon', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PackagePublishInput), graphql_name='input', default=None)),
))
    )
    publish_plan = sgqlc.types.Field(sgqlc.types.non_null('PublishPackageResult'), graphql_name='publishPlan', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PackagePublishInput), graphql_name='input', default=None)),
))
    )
    purge_customer_cache = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='purgeCustomerCache', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ClearCustomerPersistentCacheInput), graphql_name='input', default=None)),
))
    )
    recalculate_entitlements = sgqlc.types.Field(sgqlc.types.non_null('RecalculateEntitlementsResult'), graphql_name='recalculateEntitlements', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(RecalculateEntitlementsInput), graphql_name='input', default=None)),
))
    )
    register_member = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='registerMember')
    remove_addon_draft = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='removeAddonDraft', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DiscardPackageDraftInput), graphql_name='input', default=None)),
))
    )
    remove_base_plan_from_plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='removeBasePlanFromPlan', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(RemoveBasePlanFromPlanInput), graphql_name='input', default=None)),
))
    )
    remove_compatible_addons_from_plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='removeCompatibleAddonsFromPlan', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(RemoveCompatibleAddonsFromPlanInput), graphql_name='input', default=None)),
))
    )
    remove_coupon_from_customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='removeCouponFromCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(RemoveCouponFromCustomerInput), graphql_name='input', default=None)),
))
    )
    remove_coupon_from_customer_subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='removeCouponFromCustomerSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(RemoveCouponFromCustomerSubscriptionInput), graphql_name='input', default=None)),
))
    )
    remove_experiment_from_customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='removeExperimentFromCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(RemoveExperimentFromCustomerInput), graphql_name='input', default=None)),
))
    )
    remove_experiment_from_customer_subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='removeExperimentFromCustomerSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(RemoveExperimentFromCustomerSubscriptionInput), graphql_name='input', default=None)),
))
    )
    remove_member = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='removeMember', args=sgqlc.types.ArgDict((
        ('member_id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='memberId', default=None)),
))
    )
    remove_plan_draft = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='removePlanDraft', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DiscardPackageDraftInput), graphql_name='input', default=None)),
))
    )
    report_entitlement_check_requested = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reportEntitlementCheckRequested', args=sgqlc.types.ArgDict((
        ('entitlement_check_requested', sgqlc.types.Arg(sgqlc.types.non_null(EntitlementCheckRequested), graphql_name='entitlementCheckRequested', default=None)),
))
    )
    report_event = sgqlc.types.Field(String, graphql_name='reportEvent', args=sgqlc.types.ArgDict((
        ('events', sgqlc.types.Arg(sgqlc.types.non_null(UsageEventsReportInput), graphql_name='events', default=None)),
))
    )
    report_usage = sgqlc.types.Field(sgqlc.types.non_null('UsageMeasurementWithCurrentUsage'), graphql_name='reportUsage', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ReportUsageInput), graphql_name='input', default=None)),
))
    )
    report_usage_bulk = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UsageMeasurementWithCurrentUsage'))), graphql_name='reportUsageBulk', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ReportUsageBulkInput), graphql_name='input', default=None)),
))
    )
    resend_email_verification = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='resendEmailVerification')
    resync_integration = sgqlc.types.Field(sgqlc.types.non_null('ResyncIntegrationResult'), graphql_name='resyncIntegration', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ResyncIntegrationInput), graphql_name='input', default=None)),
))
    )
    revoke_promotional_entitlement = sgqlc.types.Field(sgqlc.types.non_null('PromotionalEntitlement'), graphql_name='revokePromotionalEntitlement', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(RevokePromotionalEntitlementInput), graphql_name='input', default=None)),
))
    )
    set_base_plan_on_plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='setBasePlanOnPlan', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetBasePlanOnPlanInput), graphql_name='input', default=None)),
))
    )
    set_compatible_addons_on_plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='setCompatibleAddonsOnPlan', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetCompatibleAddonsOnPlanInput), graphql_name='input', default=None)),
))
    )
    set_coupon_on_customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='setCouponOnCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetCouponOnCustomerInput), graphql_name='input', default=None)),
))
    )
    set_coupon_on_customer_subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='setCouponOnCustomerSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetCouponOnCustomerSubscriptionInput), graphql_name='input', default=None)),
))
    )
    set_experiment_on_customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='setExperimentOnCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetExperimentOnCustomerInput), graphql_name='input', default=None)),
))
    )
    set_experiment_on_customer_subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='setExperimentOnCustomerSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetExperimentOnCustomerSubscriptionInput), graphql_name='input', default=None)),
))
    )
    set_package_pricing = sgqlc.types.Field(sgqlc.types.non_null('PackagePrice'), graphql_name='setPackagePricing', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PackagePricingInput), graphql_name='input', default=None)),
))
    )
    set_widget_configuration = sgqlc.types.Field(String, graphql_name='setWidgetConfiguration', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(WidgetConfigurationUpdateInput), graphql_name='input', default=None)),
))
    )
    start_experiment = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='startExperiment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(StartExperimentInput), graphql_name='input', default=None)),
))
    )
    stop_experiment = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='stopExperiment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(StopExperimentInput), graphql_name='input', default=None)),
))
    )
    sync_tax_rates = sgqlc.types.Field(String, graphql_name='syncTaxRates', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SyncTaxRatesInput), graphql_name='input', default=None)),
))
    )
    transfer_subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='transferSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(TransferSubscriptionInput), graphql_name='input', default=None)),
))
    )
    trigger_import_catalog = sgqlc.types.Field(sgqlc.types.non_null(AsyncTaskResult), graphql_name='triggerImportCatalog', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ImportIntegrationCatalogInput), graphql_name='input', default=None)),
))
    )
    trigger_import_customers = sgqlc.types.Field(sgqlc.types.non_null(AsyncTaskResult), graphql_name='triggerImportCustomers', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ImportIntegrationCustomersInput), graphql_name='input', default=None)),
))
    )
    trigger_plan_subscription_migration = sgqlc.types.Field(sgqlc.types.non_null('TriggerSubscriptionMigrationResult'), graphql_name='triggerPlanSubscriptionMigration', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(TriggerSubscriptionMigrationInput), graphql_name='input', default=None)),
))
    )
    unarchive_customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='unarchiveCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UnarchiveCustomerInput), graphql_name='input', default=None)),
))
    )
    unarchive_environment = sgqlc.types.Field(sgqlc.types.non_null(Environment), graphql_name='unarchiveEnvironment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UnarchiveEnvironmentInput), graphql_name='input', default=None)),
))
    )
    update_account = sgqlc.types.Field(sgqlc.types.non_null(Account), graphql_name='updateAccount', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateAccountInput), graphql_name='input', default=None)),
))
    )
    update_entitlements_order = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UpdateEntitlementsOrderDTO'))), graphql_name='updateEntitlementsOrder', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdatePackageEntitlementOrderInput), graphql_name='input', default=None)),
))
    )
    update_feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='updateFeature', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateFeatureInput), graphql_name='input', default=None)),
))
    )
    update_one_addon = sgqlc.types.Field(sgqlc.types.non_null(Addon), graphql_name='updateOneAddon', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AddonUpdateInput), graphql_name='input', default=None)),
))
    )
    update_one_coupon = sgqlc.types.Field(sgqlc.types.non_null(Coupon), graphql_name='updateOneCoupon', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateCouponInput), graphql_name='input', default=None)),
))
    )
    update_one_customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='updateOneCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateCustomerInput), graphql_name='input', default=None)),
))
    )
    update_one_environment = sgqlc.types.Field(sgqlc.types.non_null(Environment), graphql_name='updateOneEnvironment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateOneEnvironmentInput), graphql_name='input', default=None)),
))
    )
    update_one_experiment = sgqlc.types.Field(sgqlc.types.non_null(Experiment), graphql_name='updateOneExperiment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateExperimentInput), graphql_name='input', default=None)),
))
    )
    update_one_feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='updateOneFeature', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateOneFeatureInput), graphql_name='input', default=None)),
))
    )
    update_one_hook = sgqlc.types.Field(sgqlc.types.non_null(Hook), graphql_name='updateOneHook', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateOneHookInput), graphql_name='input', default=None)),
))
    )
    update_one_integration = sgqlc.types.Field(sgqlc.types.non_null(Integration), graphql_name='updateOneIntegration', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateOneIntegrationInput), graphql_name='input', default=None)),
))
    )
    update_one_package_entitlement = sgqlc.types.Field(sgqlc.types.non_null('PackageEntitlement'), graphql_name='updateOnePackageEntitlement', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateOnePackageEntitlementInput), graphql_name='input', default=None)),
))
    )
    update_one_plan = sgqlc.types.Field(sgqlc.types.non_null('Plan'), graphql_name='updateOnePlan', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PlanUpdateInput), graphql_name='input', default=None)),
))
    )
    update_one_product = sgqlc.types.Field(sgqlc.types.non_null('Product'), graphql_name='updateOneProduct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateOneProductInput), graphql_name='input', default=None)),
))
    )
    update_one_promotional_entitlement = sgqlc.types.Field(sgqlc.types.non_null('PromotionalEntitlement'), graphql_name='updateOnePromotionalEntitlement', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateOnePromotionalEntitlementInput), graphql_name='input', default=None)),
))
    )
    update_one_subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='updateOneSubscription', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateSubscriptionInput), graphql_name='input', default=None)),
))
    )
    update_user = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='updateUser', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UpdateUserInput), graphql_name='input', default=None)),
))
    )


class PackageAlreadyPublishedError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class PackageChanges(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'base_plan', 'compatible_addons', 'default_trial_config', 'description', 'display_name', 'entitlements', 'hidden_from_widgets', 'overage_prices', 'prices', 'pricing_type', 'total_changes')
    additional_meta_data = sgqlc.types.Field(AdditionalMetaDataChange, graphql_name='additionalMetaData')
    base_plan = sgqlc.types.Field(BasePlanChange, graphql_name='basePlan')
    compatible_addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PlanCompatibleAddonChange')), graphql_name='compatibleAddons')
    default_trial_config = sgqlc.types.Field(DefaultTrialConfigChange, graphql_name='defaultTrialConfig')
    description = sgqlc.types.Field('StringChangeDTO', graphql_name='description')
    display_name = sgqlc.types.Field('StringChangeDTO', graphql_name='displayName')
    entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlementChange'))), graphql_name='entitlements')
    hidden_from_widgets = sgqlc.types.Field(HiddenFromWidgetsChange, graphql_name='hiddenFromWidgets')
    overage_prices = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PackagePriceChange'))), graphql_name='overagePrices')
    prices = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PackagePriceChange'))), graphql_name='prices')
    pricing_type = sgqlc.types.Field('PricingTypeChange', graphql_name='pricingType')
    total_changes = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalChanges')


class PackageDTO(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'billing_id', 'billing_link_url', 'created_at', 'description', 'display_name', 'draft_details', 'draft_summary', 'entitlements', 'environment_id', 'hidden_from_widgets', 'id', 'is_latest', 'overage_prices', 'prices', 'pricing_type', 'product_id', 'ref_id', 'status', 'sync_states', 'type', 'updated_at', 'version_number')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_link_url = sgqlc.types.Field(String, graphql_name='billingLinkUrl')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    draft_details = sgqlc.types.Field('PackageDraftDetails', graphql_name='draftDetails')
    draft_summary = sgqlc.types.Field('PackageDraftSummary', graphql_name='draftSummary')
    entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlement')), graphql_name='entitlements')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_latest = sgqlc.types.Field(Boolean, graphql_name='isLatest')
    overage_prices = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Price')), graphql_name='overagePrices')
    prices = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Price')), graphql_name='prices')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    status = sgqlc.types.Field(sgqlc.types.non_null(PackageStatus), graphql_name='status')
    sync_states = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SyncState'))), graphql_name='syncStates')
    type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='type')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='versionNumber')


class PackageDraftDetails(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('affected_child_plans', 'changes', 'child_plans_with_draft', 'customers_affected', 'updated_at', 'updated_by', 'version')
    affected_child_plans = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Plan')), graphql_name='affectedChildPlans')
    changes = sgqlc.types.Field(PackageChanges, graphql_name='changes')
    child_plans_with_draft = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Plan')), graphql_name='childPlansWithDraft')
    customers_affected = sgqlc.types.Field(Int, graphql_name='customersAffected')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')
    updated_by = sgqlc.types.Field(String, graphql_name='updatedBy')
    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')


class PackageDraftSummary(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('updated_at', 'updated_by', 'version')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')
    updated_by = sgqlc.types.Field(String, graphql_name='updatedBy')
    version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='version')


class PackageEntitlement(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'display_name_override', 'environment_id', 'feature', 'feature_id', 'has_unlimited_usage', 'hidden_from_widgets', 'id', 'is_custom', 'meter', 'order', 'package', 'package_id', 'reset_period', 'reset_period_configuration', 'updated_at', 'usage_limit')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name_override = sgqlc.types.Field(String, graphql_name='displayNameOverride')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='feature')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_custom = sgqlc.types.Field(Boolean, graphql_name='isCustom')
    meter = sgqlc.types.Field(Meter, graphql_name='meter')
    order = sgqlc.types.Field(Float, graphql_name='order')
    package = sgqlc.types.Field(PackageDTO, graphql_name='package')
    package_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='packageId')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    reset_period_configuration = sgqlc.types.Field('ResetPeriodConfiguration', graphql_name='resetPeriodConfiguration')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class PackageEntitlementAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'package_id', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    package_id = sgqlc.types.Field(String, graphql_name='packageId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class PackageEntitlementChange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'change_type')
    after = sgqlc.types.Field(PackageEntitlement, graphql_name='after')
    before = sgqlc.types.Field(PackageEntitlement, graphql_name='before')
    change_type = sgqlc.types.Field(ChangeType, graphql_name='changeType')


class PackageEntitlementConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PackageEntitlementEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class PackageEntitlementCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'package_id', 'updated_at')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    package_id = sgqlc.types.Field(Int, graphql_name='packageId')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')


class PackageEntitlementDeleteResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'display_name_override', 'environment_id', 'feature_id', 'has_unlimited_usage', 'hidden_from_widgets', 'id', 'is_custom', 'order', 'package_id', 'reset_period', 'reset_period_configuration', 'updated_at', 'usage_limit')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name_override = sgqlc.types.Field(String, graphql_name='displayNameOverride')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    id = sgqlc.types.Field(String, graphql_name='id')
    is_custom = sgqlc.types.Field(Boolean, graphql_name='isCustom')
    order = sgqlc.types.Field(Float, graphql_name='order')
    package_id = sgqlc.types.Field(String, graphql_name='packageId')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    reset_period_configuration = sgqlc.types.Field('ResetPeriodConfiguration', graphql_name='resetPeriodConfiguration')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class PackageEntitlementEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(PackageEntitlement), graphql_name='node')


class PackageEntitlementMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'package_id', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    package_id = sgqlc.types.Field(String, graphql_name='packageId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class PackageEntitlementMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'package_id', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    package_id = sgqlc.types.Field(String, graphql_name='packageId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class PackagePrice(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('package_id', 'pricing_type')
    package_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='packageId')
    pricing_type = sgqlc.types.Field(sgqlc.types.non_null(PricingType), graphql_name='pricingType')


class PackagePriceChange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'change_type')
    after = sgqlc.types.Field('Price', graphql_name='after')
    before = sgqlc.types.Field('Price', graphql_name='before')
    change_type = sgqlc.types.Field(ChangeType, graphql_name='changeType')


class PackagePricingTypeNotSetError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class PackagePublished(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account_id', 'environment_id', 'migration_type', 'package_ref_id', 'package_type', 'package_version')
    account_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='accountId')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    migration_type = sgqlc.types.Field(sgqlc.types.non_null(PublishMigrationType), graphql_name='migrationType')
    package_ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='packageRefId')
    package_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='packageType')
    package_version = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='packageVersion')


class PageInfo(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('end_cursor', 'has_next_page', 'has_previous_page', 'start_cursor')
    end_cursor = sgqlc.types.Field(ConnectionCursor, graphql_name='endCursor')
    has_next_page = sgqlc.types.Field(Boolean, graphql_name='hasNextPage')
    has_previous_page = sgqlc.types.Field(Boolean, graphql_name='hasPreviousPage')
    start_cursor = sgqlc.types.Field(ConnectionCursor, graphql_name='startCursor')


class Paywall(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('active_subscriptions', 'configuration', 'currency', 'customer', 'paywall_calculated_price_points', 'plans', 'resource')
    active_subscriptions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CustomerSubscription)), graphql_name='activeSubscriptions')
    configuration = sgqlc.types.Field('PaywallConfiguration', graphql_name='configuration')
    currency = sgqlc.types.Field(sgqlc.types.non_null('PaywallCurrency'), graphql_name='currency')
    customer = sgqlc.types.Field(Customer, graphql_name='customer')
    paywall_calculated_price_points = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PaywallPricePoint')), graphql_name='paywallCalculatedPricePoints')
    plans = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Plan'))), graphql_name='plans')
    resource = sgqlc.types.Field(CustomerResource, graphql_name='resource')


class PaywallAddon(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'billing_id', 'description', 'display_name', 'entitlements', 'prices', 'pricing_type', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Entitlement))), graphql_name='entitlements')
    prices = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PaywallPrice'))), graphql_name='prices')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class PaywallBasePlan(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('display_name', 'ref_id')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class PaywallColorsPalette(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('background_color', 'border_color', 'current_plan_background', 'primary', 'text_color')
    background_color = sgqlc.types.Field(String, graphql_name='backgroundColor')
    border_color = sgqlc.types.Field(String, graphql_name='borderColor')
    current_plan_background = sgqlc.types.Field(String, graphql_name='currentPlanBackground')
    primary = sgqlc.types.Field(String, graphql_name='primary')
    text_color = sgqlc.types.Field(String, graphql_name='textColor')


class PaywallConfiguration(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('custom_css', 'layout', 'palette', 'typography')
    custom_css = sgqlc.types.Field(String, graphql_name='customCss')
    layout = sgqlc.types.Field('PaywallLayoutConfiguration', graphql_name='layout')
    palette = sgqlc.types.Field(PaywallColorsPalette, graphql_name='palette')
    typography = sgqlc.types.Field('TypographyConfiguration', graphql_name='typography')


class PaywallCurrency(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'symbol')
    code = sgqlc.types.Field(sgqlc.types.non_null(Currency), graphql_name='code')
    symbol = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='symbol')


class PaywallLayoutConfiguration(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('alignment', 'plan_margin', 'plan_padding', 'plan_width')
    alignment = sgqlc.types.Field(Alignment, graphql_name='alignment')
    plan_margin = sgqlc.types.Field(Float, graphql_name='planMargin')
    plan_padding = sgqlc.types.Field(Float, graphql_name='planPadding')
    plan_width = sgqlc.types.Field(Float, graphql_name='planWidth')


class PaywallPlan(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'base_plan', 'billing_id', 'compatible_addons', 'default_trial_config', 'description', 'display_name', 'entitlements', 'inherited_entitlements', 'prices', 'pricing_type', 'product', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    base_plan = sgqlc.types.Field(PaywallBasePlan, graphql_name='basePlan')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    compatible_addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PaywallAddon)), graphql_name='compatibleAddons')
    default_trial_config = sgqlc.types.Field(DefaultTrialConfig, graphql_name='defaultTrialConfig')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Entitlement)), graphql_name='entitlements')
    inherited_entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Entitlement)), graphql_name='inheritedEntitlements')
    prices = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PaywallPrice'))), graphql_name='prices')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product = sgqlc.types.Field(sgqlc.types.non_null('PaywallProduct'), graphql_name='product')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class PaywallPrice(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_country_code', 'billing_id', 'billing_model', 'billing_period', 'feature', 'feature_id', 'max_unit_quantity', 'min_unit_quantity', 'price', 'tiers', 'tiers_mode')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_model = sgqlc.types.Field(sgqlc.types.non_null(BillingModel), graphql_name='billingModel')
    billing_period = sgqlc.types.Field(sgqlc.types.non_null(BillingPeriod), graphql_name='billingPeriod')
    feature = sgqlc.types.Field(EntitlementFeature, graphql_name='feature')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    max_unit_quantity = sgqlc.types.Field(Float, graphql_name='maxUnitQuantity')
    min_unit_quantity = sgqlc.types.Field(Float, graphql_name='minUnitQuantity')
    price = sgqlc.types.Field(Money, graphql_name='price')
    tiers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PriceTier')), graphql_name='tiers')
    tiers_mode = sgqlc.types.Field(TiersMode, graphql_name='tiersMode')


class PaywallPricePoint(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_charges_may_apply', 'amount', 'billing_country_code', 'billing_period', 'currency', 'feature', 'plan_id')
    additional_charges_may_apply = sgqlc.types.Field(Boolean, graphql_name='additionalChargesMayApply')
    amount = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='amount')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_period = sgqlc.types.Field(sgqlc.types.non_null(BillingPeriod), graphql_name='billingPeriod')
    currency = sgqlc.types.Field(sgqlc.types.non_null(Currency), graphql_name='currency')
    feature = sgqlc.types.Field(Feature, graphql_name='feature')
    plan_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planId')


class PaywallProduct(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'description', 'display_name', 'ref_id')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class Plan(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'aws_marketplace_plan_dimension', 'base_plan', 'billing_id', 'billing_link_url', 'compatible_addons', 'created_at', 'default_trial_config', 'description', 'display_name', 'draft_details', 'draft_summary', 'entitlements', 'environment', 'environment_id', 'hidden_from_widgets', 'id', 'inherited_entitlements', 'is_latest', 'is_parent', 'overage_prices', 'prices', 'pricing_type', 'product', 'product_id', 'ref_id', 'status', 'sync_states', 'type', 'updated_at', 'version_number')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    aws_marketplace_plan_dimension = sgqlc.types.Field(String, graphql_name='awsMarketplacePlanDimension')
    base_plan = sgqlc.types.Field('Plan', graphql_name='basePlan')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_link_url = sgqlc.types.Field(String, graphql_name='billingLinkUrl')
    compatible_addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Addon)), graphql_name='compatibleAddons', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(AddonFilter, graphql_name='filter', default={})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AddonSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    default_trial_config = sgqlc.types.Field(DefaultTrialConfig, graphql_name='defaultTrialConfig')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    draft_details = sgqlc.types.Field(PackageDraftDetails, graphql_name='draftDetails')
    draft_summary = sgqlc.types.Field(PackageDraftSummary, graphql_name='draftSummary')
    entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PackageEntitlement)), graphql_name='entitlements')
    environment = sgqlc.types.Field(sgqlc.types.non_null(Environment), graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    hidden_from_widgets = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(WidgetType)), graphql_name='hiddenFromWidgets')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    inherited_entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PackageEntitlement)), graphql_name='inheritedEntitlements', args=sgqlc.types.ArgDict((
        ('include_overridden', sgqlc.types.Arg(Boolean, graphql_name='includeOverridden', default=False)),
))
    )
    is_latest = sgqlc.types.Field(Boolean, graphql_name='isLatest')
    is_parent = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isParent')
    overage_prices = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Price')), graphql_name='overagePrices')
    prices = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Price')), graphql_name='prices')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product = sgqlc.types.Field(sgqlc.types.non_null('Product'), graphql_name='product')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    status = sgqlc.types.Field(sgqlc.types.non_null(PackageStatus), graphql_name='status')
    sync_states = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SyncState')), graphql_name='syncStates')
    type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='type')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='versionNumber')


class PlanAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    is_latest = sgqlc.types.Field(Boolean, graphql_name='isLatest')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(Int, graphql_name='versionNumber')


class PlanAvgAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('version_number',)
    version_number = sgqlc.types.Field(Float, graphql_name='versionNumber')


class PlanCompatibleAddonChange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'change_type')
    after = sgqlc.types.Field(Addon, graphql_name='after')
    before = sgqlc.types.Field(Addon, graphql_name='before')
    change_type = sgqlc.types.Field(ChangeType, graphql_name='changeType')


class PlanConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PlanEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class PlanCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_latest', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    billing_id = sgqlc.types.Field(Int, graphql_name='billingId')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    description = sgqlc.types.Field(Int, graphql_name='description')
    display_name = sgqlc.types.Field(Int, graphql_name='displayName')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    is_latest = sgqlc.types.Field(Int, graphql_name='isLatest')
    pricing_type = sgqlc.types.Field(Int, graphql_name='pricingType')
    product_id = sgqlc.types.Field(Int, graphql_name='productId')
    ref_id = sgqlc.types.Field(Int, graphql_name='refId')
    status = sgqlc.types.Field(Int, graphql_name='status')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(Int, graphql_name='versionNumber')


class PlanEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Plan), graphql_name='node')


class PlanMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(Int, graphql_name='versionNumber')


class PlanMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'pricing_type', 'product_id', 'ref_id', 'status', 'updated_at', 'version_number')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    pricing_type = sgqlc.types.Field(PricingType, graphql_name='pricingType')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    status = sgqlc.types.Field(PackageStatus, graphql_name='status')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    version_number = sgqlc.types.Field(Int, graphql_name='versionNumber')


class PlanNotFoundError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class PlanSumAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('version_number',)
    version_number = sgqlc.types.Field(Float, graphql_name='versionNumber')


class Price(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_country_code', 'billing_id', 'billing_model', 'billing_period', 'created_at', 'crm_id', 'crm_link_url', 'feature', 'feature_id', 'id', 'max_unit_quantity', 'min_unit_quantity', 'package', 'package_id', 'price', 'tiers', 'tiers_mode', 'used_in_subscriptions')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_model = sgqlc.types.Field(sgqlc.types.non_null(BillingModel), graphql_name='billingModel')
    billing_period = sgqlc.types.Field(sgqlc.types.non_null(BillingPeriod), graphql_name='billingPeriod')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(String, graphql_name='crmLinkUrl')
    feature = sgqlc.types.Field(Feature, graphql_name='feature')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    max_unit_quantity = sgqlc.types.Field(Float, graphql_name='maxUnitQuantity')
    min_unit_quantity = sgqlc.types.Field(Float, graphql_name='minUnitQuantity')
    package = sgqlc.types.Field(sgqlc.types.non_null(PackageDTO), graphql_name='package')
    package_id = sgqlc.types.Field(String, graphql_name='packageId')
    price = sgqlc.types.Field(Money, graphql_name='price')
    tiers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PriceTier')), graphql_name='tiers')
    tiers_mode = sgqlc.types.Field(TiersMode, graphql_name='tiersMode')
    used_in_subscriptions = sgqlc.types.Field(Boolean, graphql_name='usedInSubscriptions')


class PriceAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'billing_model', 'billing_period', 'created_at', 'id', 'tiers_mode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(String, graphql_name='id')
    tiers_mode = sgqlc.types.Field(TiersMode, graphql_name='tiersMode')


class PriceCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'billing_model', 'billing_period', 'created_at', 'id', 'tiers_mode')
    billing_id = sgqlc.types.Field(Int, graphql_name='billingId')
    billing_model = sgqlc.types.Field(Int, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(Int, graphql_name='billingPeriod')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    id = sgqlc.types.Field(Int, graphql_name='id')
    tiers_mode = sgqlc.types.Field(Int, graphql_name='tiersMode')


class PriceDeleteResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_country_code', 'billing_id', 'billing_model', 'billing_period', 'created_at', 'crm_id', 'crm_link_url', 'feature', 'feature_id', 'id', 'max_unit_quantity', 'min_unit_quantity', 'package_id', 'price', 'tiers', 'tiers_mode', 'used_in_subscriptions')
    billing_country_code = sgqlc.types.Field(String, graphql_name='billingCountryCode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    crm_id = sgqlc.types.Field(String, graphql_name='crmId')
    crm_link_url = sgqlc.types.Field(String, graphql_name='crmLinkUrl')
    feature = sgqlc.types.Field(Feature, graphql_name='feature')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    id = sgqlc.types.Field(String, graphql_name='id')
    max_unit_quantity = sgqlc.types.Field(Float, graphql_name='maxUnitQuantity')
    min_unit_quantity = sgqlc.types.Field(Float, graphql_name='minUnitQuantity')
    package_id = sgqlc.types.Field(String, graphql_name='packageId')
    price = sgqlc.types.Field(Money, graphql_name='price')
    tiers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('PriceTier')), graphql_name='tiers')
    tiers_mode = sgqlc.types.Field(TiersMode, graphql_name='tiersMode')
    used_in_subscriptions = sgqlc.types.Field(Boolean, graphql_name='usedInSubscriptions')


class PriceEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Price), graphql_name='node')


class PriceEntitlement(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('description', 'feature', 'feature_id', 'has_soft_limit', 'has_unlimited_usage', 'package', 'package_id', 'reset_period', 'reset_period_configuration', 'updated_at', 'usage_limit')
    description = sgqlc.types.Field(String, graphql_name='description')
    feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='feature')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    has_soft_limit = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasSoftLimit')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    package = sgqlc.types.Field(sgqlc.types.non_null(PackageDTO), graphql_name='package')
    package_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='packageId')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    reset_period_configuration = sgqlc.types.Field('ResetPeriodConfiguration', graphql_name='resetPeriodConfiguration')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class PriceMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'billing_model', 'billing_period', 'created_at', 'id', 'tiers_mode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(String, graphql_name='id')
    tiers_mode = sgqlc.types.Field(TiersMode, graphql_name='tiersMode')


class PriceMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'billing_model', 'billing_period', 'created_at', 'id', 'tiers_mode')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(String, graphql_name='id')
    tiers_mode = sgqlc.types.Field(TiersMode, graphql_name='tiersMode')


class PriceNotFoundError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class PriceTier(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('flat_price', 'unit_price', 'up_to')
    flat_price = sgqlc.types.Field(Money, graphql_name='flatPrice')
    unit_price = sgqlc.types.Field(Money, graphql_name='unitPrice')
    up_to = sgqlc.types.Field(Float, graphql_name='upTo')


class PricingTypeChange(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'change_type')
    after = sgqlc.types.Field(PricingType, graphql_name='after')
    before = sgqlc.types.Field(PricingType, graphql_name='before')
    change_type = sgqlc.types.Field(ChangeType, graphql_name='changeType')


class Product(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'addons', 'aws_marketplace_product_code', 'aws_marketplace_product_id', 'created_at', 'description', 'display_name', 'downgrade_plan', 'environment', 'environment_id', 'has_subscriptions', 'id', 'is_default_product', 'multiple_subscriptions', 'plans', 'product_settings', 'ref_id', 'subscription_start_plan', 'updated_at')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    addons = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Addon))), graphql_name='addons')
    aws_marketplace_product_code = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductCode')
    aws_marketplace_product_id = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductId')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    downgrade_plan = sgqlc.types.Field(Plan, graphql_name='downgradePlan')
    environment = sgqlc.types.Field(Environment, graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    has_subscriptions = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasSubscriptions')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_default_product = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isDefaultProduct')
    multiple_subscriptions = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='multipleSubscriptions')
    plans = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Plan))), graphql_name='plans')
    product_settings = sgqlc.types.Field(sgqlc.types.non_null('ProductSettings'), graphql_name='productSettings')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    subscription_start_plan = sgqlc.types.Field(Plan, graphql_name='subscriptionStartPlan')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')


class ProductAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('aws_marketplace_product_code', 'aws_marketplace_product_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_default_product', 'ref_id', 'updated_at')
    aws_marketplace_product_code = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductCode')
    aws_marketplace_product_id = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    is_default_product = sgqlc.types.Field(Boolean, graphql_name='isDefaultProduct')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class ProductCatalogDump(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('dump',)
    dump = sgqlc.types.Field(sgqlc.types.non_null(JSON), graphql_name='dump')


class ProductConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ProductEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class ProductCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('aws_marketplace_product_code', 'aws_marketplace_product_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_default_product', 'ref_id', 'updated_at')
    aws_marketplace_product_code = sgqlc.types.Field(Int, graphql_name='awsMarketplaceProductCode')
    aws_marketplace_product_id = sgqlc.types.Field(Int, graphql_name='awsMarketplaceProductId')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    description = sgqlc.types.Field(Int, graphql_name='description')
    display_name = sgqlc.types.Field(Int, graphql_name='displayName')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    is_default_product = sgqlc.types.Field(Int, graphql_name='isDefaultProduct')
    ref_id = sgqlc.types.Field(Int, graphql_name='refId')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')


class ProductDeleteResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('additional_meta_data', 'addons', 'aws_marketplace_product_code', 'aws_marketplace_product_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'is_default_product', 'multiple_subscriptions', 'plans', 'product_settings', 'ref_id', 'updated_at')
    additional_meta_data = sgqlc.types.Field(JSON, graphql_name='additionalMetaData')
    addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Addon)), graphql_name='addons')
    aws_marketplace_product_code = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductCode')
    aws_marketplace_product_id = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    is_default_product = sgqlc.types.Field(Boolean, graphql_name='isDefaultProduct')
    multiple_subscriptions = sgqlc.types.Field(Boolean, graphql_name='multipleSubscriptions')
    plans = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Plan)), graphql_name='plans')
    product_settings = sgqlc.types.Field('ProductSettings', graphql_name='productSettings')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class ProductEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(Product), graphql_name='node')


class ProductMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('aws_marketplace_product_code', 'aws_marketplace_product_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'ref_id', 'updated_at')
    aws_marketplace_product_code = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductCode')
    aws_marketplace_product_id = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class ProductMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('aws_marketplace_product_code', 'aws_marketplace_product_id', 'created_at', 'description', 'display_name', 'environment_id', 'id', 'ref_id', 'updated_at')
    aws_marketplace_product_code = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductCode')
    aws_marketplace_product_id = sgqlc.types.Field(String, graphql_name='awsMarketplaceProductId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    display_name = sgqlc.types.Field(String, graphql_name='displayName')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    ref_id = sgqlc.types.Field(String, graphql_name='refId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class ProductSettings(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('downgrade_plan', 'downgrade_plan_id', 'subscription_cancellation_time', 'subscription_end_setup', 'subscription_start_plan', 'subscription_start_plan_id', 'subscription_start_setup')
    downgrade_plan = sgqlc.types.Field(Plan, graphql_name='downgradePlan')
    downgrade_plan_id = sgqlc.types.Field(String, graphql_name='downgradePlanId')
    subscription_cancellation_time = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionCancellationTime), graphql_name='subscriptionCancellationTime')
    subscription_end_setup = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionEndSetup), graphql_name='subscriptionEndSetup')
    subscription_start_plan = sgqlc.types.Field(Plan, graphql_name='subscriptionStartPlan')
    subscription_start_plan_id = sgqlc.types.Field(String, graphql_name='subscriptionStartPlanId')
    subscription_start_setup = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionStartSetup), graphql_name='subscriptionStartSetup')


class PromotionCodeCustomerNotFirstPurchase(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class PromotionCodeMaxRedemptionsReached(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class PromotionCodeMinimumAmountNotReached(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class PromotionCodeNotActive(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class PromotionCodeNotForCustomer(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class PromotionCodeNotFound(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class PromotionalEntitlement(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'customer', 'description', 'end_date', 'environment_id', 'feature', 'feature_id', 'has_soft_limit', 'has_unlimited_usage', 'id', 'is_visible', 'meter', 'period', 'reset_period', 'reset_period_configuration', 'start_date', 'status', 'unlimited', 'updated_at', 'usage_limit')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='customer')
    description = sgqlc.types.Field(String, graphql_name='description')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='feature')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    has_soft_limit = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasSoftLimit')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_visible = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isVisible')
    meter = sgqlc.types.Field(Meter, graphql_name='meter')
    period = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlementPeriod), graphql_name='period')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    reset_period_configuration = sgqlc.types.Field('ResetPeriodConfiguration', graphql_name='resetPeriodConfiguration')
    start_date = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='startDate')
    status = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlementStatus), graphql_name='status')
    unlimited = sgqlc.types.Field(Boolean, graphql_name='unlimited')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class PromotionalEntitlementAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='status')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class PromotionalEntitlementConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PromotionalEntitlementEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class PromotionalEntitlementCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'updated_at')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    status = sgqlc.types.Field(Int, graphql_name='status')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')


class PromotionalEntitlementDeleteResponse(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'end_date', 'environment_id', 'feature_id', 'has_soft_limit', 'has_unlimited_usage', 'id', 'is_visible', 'period', 'reset_period', 'reset_period_configuration', 'start_date', 'status', 'unlimited', 'updated_at', 'usage_limit')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    has_soft_limit = sgqlc.types.Field(Boolean, graphql_name='hasSoftLimit')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    id = sgqlc.types.Field(String, graphql_name='id')
    is_visible = sgqlc.types.Field(Boolean, graphql_name='isVisible')
    period = sgqlc.types.Field(PromotionalEntitlementPeriod, graphql_name='period')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    reset_period_configuration = sgqlc.types.Field('ResetPeriodConfiguration', graphql_name='resetPeriodConfiguration')
    start_date = sgqlc.types.Field(DateTime, graphql_name='startDate')
    status = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='status')
    unlimited = sgqlc.types.Field(Boolean, graphql_name='unlimited')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class PromotionalEntitlementEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlement), graphql_name='node')


class PromotionalEntitlementMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='status')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class PromotionalEntitlementMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(PromotionalEntitlementStatus, graphql_name='status')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class ProvisionSubscriptionResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('checkout_billing_id', 'checkout_url', 'entitlements', 'id', 'is_scheduled', 'status', 'subscription')
    checkout_billing_id = sgqlc.types.Field(String, graphql_name='checkoutBillingId')
    checkout_url = sgqlc.types.Field(String, graphql_name='checkoutUrl')
    entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Entitlement)), graphql_name='entitlements')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_scheduled = sgqlc.types.Field(Boolean, graphql_name='isScheduled')
    status = sgqlc.types.Field(sgqlc.types.non_null(ProvisionSubscriptionStatus), graphql_name='status')
    subscription = sgqlc.types.Field(CustomerSubscription, graphql_name='subscription')


class ProvisionedCustomer(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('customer', 'entitlements', 'subscription', 'subscription_decision_strategy', 'subscription_strategy_decision')
    customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='customer')
    entitlements = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Entitlement)), graphql_name='entitlements')
    subscription = sgqlc.types.Field(CustomerSubscription, graphql_name='subscription')
    subscription_decision_strategy = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionDecisionStrategy), graphql_name='subscriptionDecisionStrategy')
    subscription_strategy_decision = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionDecisionStrategy), graphql_name='subscriptionStrategyDecision')


class PublishPackageResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('task_id',)
    task_id = sgqlc.types.Field(String, graphql_name='taskId')


class Query(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('addons', 'aggregated_events_by_customer', 'cached_entitlements', 'checkout_state', 'coupon', 'coupons', 'current_environment', 'current_user', 'customer_portal', 'customer_resources', 'customer_subscriptions', 'customers', 'does_feature_exist', 'dump_environment_for_merge_comparison', 'dump_environment_product_catalog', 'entitlement', 'entitlements', 'environments', 'events_fields', 'experiment', 'experiments', 'feature_associated_latest_packages', 'features', 'fetch_account', 'get_active_subscriptions', 'get_addon_by_ref_id', 'get_aws_external_id', 'get_customer_by_ref_id', 'get_experiment_stats', 'get_paywall', 'get_plan_by_ref_id', 'hook', 'hooks', 'import_integration_tasks', 'integrations', 'list_aws_product_dimensions', 'list_aws_products', 'members', 'mock_paywall', 'package_entitlements', 'paywall', 'plans', 'products', 'promotional_entitlements', 'sdk_configuration', 'send_test_hook', 'stripe_customers', 'stripe_products', 'stripe_subscriptions', 'subscription_entitlements', 'subscription_migration_tasks', 'test_hook_data', 'usage_events', 'usage_history', 'usage_measurements', 'validate_merge_environment', 'widget_configuration')
    addons = sgqlc.types.Field(sgqlc.types.non_null(AddonConnection), graphql_name='addons', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(AddonFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AddonSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    aggregated_events_by_customer = sgqlc.types.Field(sgqlc.types.non_null(AggregatedEventsByCustomer), graphql_name='aggregatedEventsByCustomer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(AggregatedEventsByCustomerInput), graphql_name='input', default=None)),
))
    )
    cached_entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Entitlement))), graphql_name='cachedEntitlements', args=sgqlc.types.ArgDict((
        ('query', sgqlc.types.Arg(sgqlc.types.non_null(FetchEntitlementsQuery), graphql_name='query', default=None)),
))
    )
    checkout_state = sgqlc.types.Field(sgqlc.types.non_null(CheckoutState), graphql_name='checkoutState', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CheckoutStateInput), graphql_name='input', default=None)),
))
    )
    coupon = sgqlc.types.Field(Coupon, graphql_name='coupon', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='id', default=None)),
))
    )
    coupons = sgqlc.types.Field(sgqlc.types.non_null(CouponConnection), graphql_name='coupons', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(CouponFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(CouponSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    current_environment = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='currentEnvironment')
    current_user = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='currentUser')
    customer_portal = sgqlc.types.Field(sgqlc.types.non_null(CustomerPortal), graphql_name='customerPortal', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CustomerPortalInput), graphql_name='input', default=None)),
))
    )
    customer_resources = sgqlc.types.Field(sgqlc.types.non_null(CustomerResourceConnection), graphql_name='customerResources', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(CustomerResourceFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(CustomerResourceSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    customer_subscriptions = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscriptionConnection), graphql_name='customerSubscriptions', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(CustomerSubscriptionFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(CustomerSubscriptionSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    customers = sgqlc.types.Field(sgqlc.types.non_null(CustomerConnection), graphql_name='customers', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(CustomerFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(CustomerSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    does_feature_exist = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='doesFeatureExist', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DoesFeatureExist), graphql_name='input', default=None)),
))
    )
    dump_environment_for_merge_comparison = sgqlc.types.Field(sgqlc.types.non_null(DumpEnvironmentForMergeComparison), graphql_name='dumpEnvironmentForMergeComparison', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DumpEnvironmentForForMergeComparisonInput), graphql_name='input', default=None)),
))
    )
    dump_environment_product_catalog = sgqlc.types.Field(sgqlc.types.non_null(ProductCatalogDump), graphql_name='dumpEnvironmentProductCatalog', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DumpEnvironmentProductCatalogInput), graphql_name='input', default=None)),
))
    )
    entitlement = sgqlc.types.Field(sgqlc.types.non_null(Entitlement), graphql_name='entitlement', args=sgqlc.types.ArgDict((
        ('query', sgqlc.types.Arg(sgqlc.types.non_null(FetchEntitlementQuery), graphql_name='query', default=None)),
))
    )
    entitlements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(EntitlementWithSummary))), graphql_name='entitlements', args=sgqlc.types.ArgDict((
        ('query', sgqlc.types.Arg(sgqlc.types.non_null(FetchEntitlementsQuery), graphql_name='query', default=None)),
))
    )
    environments = sgqlc.types.Field(sgqlc.types.non_null(EnvironmentConnection), graphql_name='environments', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(EnvironmentFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(EnvironmentSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    events_fields = sgqlc.types.Field(sgqlc.types.non_null(EventsFields), graphql_name='eventsFields', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(EventsFieldsInput), graphql_name='input', default=None)),
))
    )
    experiment = sgqlc.types.Field(Experiment, graphql_name='experiment', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='id', default=None)),
))
    )
    experiments = sgqlc.types.Field(sgqlc.types.non_null(ExperimentConnection), graphql_name='experiments', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ExperimentFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ExperimentSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    feature_associated_latest_packages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PackageDTO))), graphql_name='featureAssociatedLatestPackages', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(FeatureAssociatedLatestPackages), graphql_name='input', default=None)),
))
    )
    features = sgqlc.types.Field(sgqlc.types.non_null(FeatureConnection), graphql_name='features', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(FeatureFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(FeatureSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    fetch_account = sgqlc.types.Field(Account, graphql_name='fetchAccount')
    get_active_subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CustomerSubscription))), graphql_name='getActiveSubscriptions', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(GetActiveSubscriptionsInput), graphql_name='input', default=None)),
))
    )
    get_addon_by_ref_id = sgqlc.types.Field(Addon, graphql_name='getAddonByRefId', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(GetPackageByRefIdInput), graphql_name='input', default=None)),
))
    )
    get_aws_external_id = sgqlc.types.Field(sgqlc.types.non_null(GetAwsExternalIdResult), graphql_name='getAwsExternalId')
    get_customer_by_ref_id = sgqlc.types.Field(Customer, graphql_name='getCustomerByRefId', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(GetCustomerByRefIdInput), graphql_name='input', default=None)),
))
    )
    get_experiment_stats = sgqlc.types.Field(sgqlc.types.non_null(ExperimentStats), graphql_name='getExperimentStats', args=sgqlc.types.ArgDict((
        ('query', sgqlc.types.Arg(sgqlc.types.non_null(ExperimentStatsQuery), graphql_name='query', default=None)),
))
    )
    get_paywall = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Plan))), graphql_name='getPaywall', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(GetPaywallInput), graphql_name='input', default=None)),
))
    )
    get_plan_by_ref_id = sgqlc.types.Field(Plan, graphql_name='getPlanByRefId', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(GetPackageByRefIdInput), graphql_name='input', default=None)),
))
    )
    hook = sgqlc.types.Field(Hook, graphql_name='hook', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='id', default=None)),
))
    )
    hooks = sgqlc.types.Field(sgqlc.types.non_null(HookConnection), graphql_name='hooks', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(HookFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(HookSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    import_integration_tasks = sgqlc.types.Field(sgqlc.types.non_null(ImportIntegrationTaskConnection), graphql_name='importIntegrationTasks', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ImportIntegrationTaskFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ImportIntegrationTaskSort)), graphql_name='sorting', default=[])),
))
    )
    integrations = sgqlc.types.Field(sgqlc.types.non_null(IntegrationConnection), graphql_name='integrations', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(IntegrationFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(IntegrationSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    list_aws_product_dimensions = sgqlc.types.Field(sgqlc.types.non_null(ListAwsProductDimensionsDTO), graphql_name='listAwsProductDimensions', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ListAwsProductDimensionsInput), graphql_name='input', default=None)),
))
    )
    list_aws_products = sgqlc.types.Field(sgqlc.types.non_null(ListAwsProductsResult), graphql_name='listAwsProducts', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ListAwsProductsInput), graphql_name='input', default=None)),
))
    )
    members = sgqlc.types.Field(sgqlc.types.non_null(MemberConnection), graphql_name='members', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(MemberFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(MemberSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    mock_paywall = sgqlc.types.Field(sgqlc.types.non_null(MockPaywall), graphql_name='mockPaywall', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(GetPaywallInput), graphql_name='input', default=None)),
))
    )
    package_entitlements = sgqlc.types.Field(sgqlc.types.non_null(PackageEntitlementConnection), graphql_name='packageEntitlements', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(PackageEntitlementFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(PackageEntitlementSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    paywall = sgqlc.types.Field(sgqlc.types.non_null(Paywall), graphql_name='paywall', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(GetPaywallInput), graphql_name='input', default=None)),
))
    )
    plans = sgqlc.types.Field(sgqlc.types.non_null(PlanConnection), graphql_name='plans', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(PlanFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(PlanSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    products = sgqlc.types.Field(sgqlc.types.non_null(ProductConnection), graphql_name='products', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(ProductFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ProductSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    promotional_entitlements = sgqlc.types.Field(sgqlc.types.non_null(PromotionalEntitlementConnection), graphql_name='promotionalEntitlements', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(PromotionalEntitlementFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(PromotionalEntitlementSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    sdk_configuration = sgqlc.types.Field('SdkConfiguration', graphql_name='sdkConfiguration')
    send_test_hook = sgqlc.types.Field(sgqlc.types.non_null('TestHookResult'), graphql_name='sendTestHook', args=sgqlc.types.ArgDict((
        ('test_hook_input', sgqlc.types.Arg(sgqlc.types.non_null(TestHookInput), graphql_name='testHookInput', default=None)),
))
    )
    stripe_customers = sgqlc.types.Field(sgqlc.types.non_null('StripeCustomerSearchResult'), graphql_name='stripeCustomers', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(StripeCustomerSearchInput), graphql_name='input', default=None)),
))
    )
    stripe_products = sgqlc.types.Field(sgqlc.types.non_null('StripeProductSearchResult'), graphql_name='stripeProducts', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(StripeProductSearchInput), graphql_name='input', default=None)),
))
    )
    stripe_subscriptions = sgqlc.types.Field(sgqlc.types.non_null('StripeSubscriptionSearchResult'), graphql_name='stripeSubscriptions', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(StripeSubscriptionSearchInput), graphql_name='input', default=None)),
))
    )
    subscription_entitlements = sgqlc.types.Field(sgqlc.types.non_null('SubscriptionEntitlementConnection'), graphql_name='subscriptionEntitlements', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(SubscriptionEntitlementFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionEntitlementSort)), graphql_name='sorting', default=[])),
))
    )
    subscription_migration_tasks = sgqlc.types.Field(sgqlc.types.non_null('SubscriptionMigrationTaskConnection'), graphql_name='subscriptionMigrationTasks', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(SubscriptionMigrationTaskFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(SubscriptionMigrationTaskSort)), graphql_name='sorting', default=[])),
))
    )
    test_hook_data = sgqlc.types.Field(sgqlc.types.non_null('TestHook'), graphql_name='testHookData', args=sgqlc.types.ArgDict((
        ('event_log_type', sgqlc.types.Arg(sgqlc.types.non_null(EventLogType), graphql_name='eventLogType', default=None)),
))
    )
    usage_events = sgqlc.types.Field(sgqlc.types.non_null('UsageEventsPreview'), graphql_name='usageEvents', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UsageEventsInput), graphql_name='input', default=None)),
))
    )
    usage_history = sgqlc.types.Field(sgqlc.types.non_null('UsageHistory'), graphql_name='usageHistory', args=sgqlc.types.ArgDict((
        ('usage_history_input', sgqlc.types.Arg(sgqlc.types.non_null(UsageHistoryInput), graphql_name='usageHistoryInput', default=None)),
))
    )
    usage_measurements = sgqlc.types.Field(sgqlc.types.non_null('UsageMeasurementConnection'), graphql_name='usageMeasurements', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(UsageMeasurementFilter, graphql_name='filter', default={})),
        ('paging', sgqlc.types.Arg(CursorPaging, graphql_name='paging', default={'first': 10})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(UsageMeasurementSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    validate_merge_environment = sgqlc.types.Field(sgqlc.types.non_null('ValidateMergeEnvironment'), graphql_name='validateMergeEnvironment', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ValidateMergeEnvironmentInput), graphql_name='input', default=None)),
))
    )
    widget_configuration = sgqlc.types.Field(sgqlc.types.non_null('WidgetConfiguration'), graphql_name='widgetConfiguration', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(GetWidgetConfigurationInput), graphql_name='input', default=None)),
))
    )


class RecalculateEntitlementsResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('task_id',)
    task_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='taskId')


class ResyncIntegrationResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('task_id',)
    task_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='taskId')


class SdkConfiguration(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('is_widget_watermark_enabled', 'sentry_dsn')
    is_widget_watermark_enabled = sgqlc.types.Field(Boolean, graphql_name='isWidgetWatermarkEnabled')
    sentry_dsn = sgqlc.types.Field(String, graphql_name='sentryDsn')


class StringChangeDTO(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('after', 'before', 'change_type')
    after = sgqlc.types.Field(String, graphql_name='after')
    before = sgqlc.types.Field(String, graphql_name='before')
    change_type = sgqlc.types.Field(ChangeType, graphql_name='changeType')


class StripeCredentials(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account_display_name', 'account_id', 'is_test_mode')
    account_display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='accountDisplayName')
    account_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='accountId')
    is_test_mode = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isTestMode')


class StripeCustomer(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'email', 'environment_id', 'id', 'is_synced', 'name', 'subscription_plan_name', 'subscriptions_count')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdAt')
    email = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='email')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_synced = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isSynced')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    subscription_plan_name = sgqlc.types.Field(String, graphql_name='subscriptionPlanName')
    subscriptions_count = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='subscriptionsCount')


class StripeCustomerIsDeleted(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'code', 'is_validation_error')
    billing_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='billingId')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class StripeCustomerSearchResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('customers', 'next_page', 'total_count')
    customers = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(StripeCustomer))), graphql_name='customers')
    next_page = sgqlc.types.Field(String, graphql_name='nextPage')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class StripeProduct(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('environment_id', 'id', 'is_synced', 'name', 'not_supported_for_import', 'prices', 'updated_at')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    is_synced = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isSynced')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    not_supported_for_import = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='notSupportedForImport')
    prices = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('StripeProductPrice'))), graphql_name='prices')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')


class StripeProductPrice(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('amount', 'billing_period')
    amount = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='amount')
    billing_period = sgqlc.types.Field(BillingPeriod, graphql_name='billingPeriod')


class StripeProductSearchResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('next_page', 'products', 'total_count', 'usage_based_product_present')
    next_page = sgqlc.types.Field(String, graphql_name='nextPage')
    products = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(StripeProduct))), graphql_name='products')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')
    usage_based_product_present = sgqlc.types.Field(Boolean, graphql_name='usageBasedProductPresent')


class StripeSubscription(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')


class StripeSubscriptionSearchResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('next_page', 'subscriptions', 'total_count')
    next_page = sgqlc.types.Field(String, graphql_name='nextPage')
    subscriptions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(StripeSubscription))), graphql_name='subscriptions')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class Subscription(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('entitlements_updated', 'package_published', 'usage_updated')
    entitlements_updated = sgqlc.types.Field(sgqlc.types.non_null(EntitlementsUpdated), graphql_name='entitlementsUpdated')
    package_published = sgqlc.types.Field(sgqlc.types.non_null(PackagePublished), graphql_name='packagePublished')
    usage_updated = sgqlc.types.Field(sgqlc.types.non_null('UsageUpdated'), graphql_name='usageUpdated')


class SubscriptionAddon(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('addon', 'created_at', 'id', 'price', 'quantity', 'subscription', 'updated_at')
    addon = sgqlc.types.Field(sgqlc.types.non_null(Addon), graphql_name='addon')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    price = sgqlc.types.Field(Price, graphql_name='price')
    quantity = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='quantity')
    subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='subscription')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')


class SubscriptionAddonAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'id', 'quantity', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(String, graphql_name='id')
    quantity = sgqlc.types.Field(Float, graphql_name='quantity')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class SubscriptionAddonAvgAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('quantity',)
    quantity = sgqlc.types.Field(Float, graphql_name='quantity')


class SubscriptionAddonCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'id', 'quantity', 'updated_at')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    id = sgqlc.types.Field(Int, graphql_name='id')
    quantity = sgqlc.types.Field(Int, graphql_name='quantity')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')


class SubscriptionAddonEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionAddon), graphql_name='node')


class SubscriptionAddonMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'id', 'quantity', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(String, graphql_name='id')
    quantity = sgqlc.types.Field(Float, graphql_name='quantity')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class SubscriptionAddonMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'id', 'quantity', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    id = sgqlc.types.Field(String, graphql_name='id')
    quantity = sgqlc.types.Field(Float, graphql_name='quantity')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class SubscriptionAddonSumAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('quantity',)
    quantity = sgqlc.types.Field(Float, graphql_name='quantity')


class SubscriptionAlreadyCanceledOrExpired(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id', 'status')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    status = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionStatus), graphql_name='status')


class SubscriptionCoupon(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('discount_value', 'environment_id', 'id', 'name', 'ref_id', 'type')
    discount_value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='discountValue')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')
    type = sgqlc.types.Field(sgqlc.types.non_null(CouponType), graphql_name='type')


class SubscriptionEntitlement(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'description', 'environment_id', 'feature', 'feature_id', 'has_unlimited_usage', 'id', 'meter', 'reset_period', 'reset_period_configuration', 'subscription', 'subscription_id', 'updated_at', 'usage_limit')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    description = sgqlc.types.Field(String, graphql_name='description')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='feature')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    has_unlimited_usage = sgqlc.types.Field(Boolean, graphql_name='hasUnlimitedUsage')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    meter = sgqlc.types.Field(Meter, graphql_name='meter')
    reset_period = sgqlc.types.Field(EntitlementResetPeriod, graphql_name='resetPeriod')
    reset_period_configuration = sgqlc.types.Field('ResetPeriodConfiguration', graphql_name='resetPeriodConfiguration')
    subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='subscription')
    subscription_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subscriptionId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class SubscriptionEntitlementAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'subscription_id', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class SubscriptionEntitlementConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionEntitlementEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')


class SubscriptionEntitlementCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'subscription_id', 'updated_at')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    subscription_id = sgqlc.types.Field(Int, graphql_name='subscriptionId')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')


class SubscriptionEntitlementEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionEntitlement), graphql_name='node')


class SubscriptionEntitlementMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'subscription_id', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class SubscriptionEntitlementMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'subscription_id', 'updated_at')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    subscription_id = sgqlc.types.Field(String, graphql_name='subscriptionId')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')


class SubscriptionFutureUpdate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'schedule_status', 'schedule_variables', 'scheduled_execution_time', 'subscription_schedule_type', 'target_package')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    schedule_status = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionScheduleStatus), graphql_name='scheduleStatus')
    schedule_variables = sgqlc.types.Field('ScheduleVariables', graphql_name='scheduleVariables')
    scheduled_execution_time = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='scheduledExecutionTime')
    subscription_schedule_type = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionScheduleType), graphql_name='subscriptionScheduleType')
    target_package = sgqlc.types.Field(PackageDTO, graphql_name='targetPackage')


class SubscriptionInvoice(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('amount_due', 'applied_balance', 'billing_id', 'created_at', 'currency', 'ending_balance', 'error_message', 'lines', 'payment_secret', 'payment_url', 'pdf_url', 'requires_action', 'starting_balance', 'status', 'sub_total', 'sub_total_excluding_tax', 'tax', 'total', 'total_excluding_tax', 'updated_at')
    amount_due = sgqlc.types.Field(Float, graphql_name='amountDue')
    applied_balance = sgqlc.types.Field(Float, graphql_name='appliedBalance')
    billing_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='billingId')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdAt')
    currency = sgqlc.types.Field(String, graphql_name='currency')
    ending_balance = sgqlc.types.Field(Float, graphql_name='endingBalance')
    error_message = sgqlc.types.Field(String, graphql_name='errorMessage')
    lines = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(InvoiceLine)), graphql_name='lines')
    payment_secret = sgqlc.types.Field(String, graphql_name='paymentSecret')
    payment_url = sgqlc.types.Field(String, graphql_name='paymentUrl')
    pdf_url = sgqlc.types.Field(String, graphql_name='pdfUrl')
    requires_action = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='requiresAction')
    starting_balance = sgqlc.types.Field(Float, graphql_name='startingBalance')
    status = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionInvoiceStatus), graphql_name='status')
    sub_total = sgqlc.types.Field(Float, graphql_name='subTotal')
    sub_total_excluding_tax = sgqlc.types.Field(Float, graphql_name='subTotalExcludingTax')
    tax = sgqlc.types.Field(Float, graphql_name='tax')
    total = sgqlc.types.Field(Float, graphql_name='total')
    total_excluding_tax = sgqlc.types.Field(Float, graphql_name='totalExcludingTax')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')


class SubscriptionMigrationTask(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('affected_customers_count', 'created_at', 'end_date', 'environment_id', 'id', 'initiated_package_id', 'migrated_customers_count', 'packages', 'progress', 'start_date', 'status', 'task_type')
    affected_customers_count = sgqlc.types.Field(Int, graphql_name='affectedCustomersCount')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    initiated_package_id = sgqlc.types.Field(String, graphql_name='initiatedPackageId')
    migrated_customers_count = sgqlc.types.Field(Int, graphql_name='migratedCustomersCount')
    packages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PackageDTO))), graphql_name='packages', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(PackageDTOFilter, graphql_name='filter', default={})),
        ('sorting', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(PackageDTOSort)), graphql_name='sorting', default=[{'direction': 'DESC', 'field': 'createdAt'}])),
))
    )
    progress = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='progress')
    start_date = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='startDate')
    status = sgqlc.types.Field(sgqlc.types.non_null(TaskStatus), graphql_name='status')
    task_type = sgqlc.types.Field(sgqlc.types.non_null(TaskType), graphql_name='taskType')


class SubscriptionMigrationTaskAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'task_type')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(TaskStatus, graphql_name='status')
    task_type = sgqlc.types.Field(TaskType, graphql_name='taskType')


class SubscriptionMigrationTaskConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SubscriptionMigrationTaskEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')


class SubscriptionMigrationTaskCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'task_type')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    status = sgqlc.types.Field(Int, graphql_name='status')
    task_type = sgqlc.types.Field(Int, graphql_name='taskType')


class SubscriptionMigrationTaskEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionMigrationTask), graphql_name='node')


class SubscriptionMigrationTaskMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'task_type')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(TaskStatus, graphql_name='status')
    task_type = sgqlc.types.Field(TaskType, graphql_name='taskType')


class SubscriptionMigrationTaskMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id', 'status', 'task_type')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')
    status = sgqlc.types.Field(TaskStatus, graphql_name='status')
    task_type = sgqlc.types.Field(TaskType, graphql_name='taskType')


class SubscriptionMustHaveSinglePlanError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_ids')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='refIds')


class SubscriptionPreview(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_period_range', 'credits', 'discount', 'discount_amount', 'has_scheduled_updates', 'is_plan_downgrade', 'proration', 'sub_total', 'subscription', 'tax', 'tax_details', 'total', 'total_excluding_tax')
    billing_period_range = sgqlc.types.Field(sgqlc.types.non_null(DateRange), graphql_name='billingPeriodRange')
    credits = sgqlc.types.Field('SubscriptionPreviewCredits', graphql_name='credits')
    discount = sgqlc.types.Field('SubscriptionPreviewDiscount', graphql_name='discount')
    discount_amount = sgqlc.types.Field(Money, graphql_name='discountAmount')
    has_scheduled_updates = sgqlc.types.Field(Boolean, graphql_name='hasScheduledUpdates')
    is_plan_downgrade = sgqlc.types.Field(Boolean, graphql_name='isPlanDowngrade')
    proration = sgqlc.types.Field('SubscriptionPreviewProrations', graphql_name='proration')
    sub_total = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='subTotal')
    subscription = sgqlc.types.Field('SubscriptionPricePreviewDTO', graphql_name='subscription')
    tax = sgqlc.types.Field(Money, graphql_name='tax')
    tax_details = sgqlc.types.Field('SubscriptionPreviewTaxDetails', graphql_name='taxDetails')
    total = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='total')
    total_excluding_tax = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='totalExcludingTax')


class SubscriptionPreviewCredits(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('initial', 'remaining', 'used')
    initial = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='initial')
    remaining = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='remaining')
    used = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='used')


class SubscriptionPreviewDiscount(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('duration_in_months', 'duration_type', 'type', 'value')
    duration_in_months = sgqlc.types.Field(Float, graphql_name='durationInMonths')
    duration_type = sgqlc.types.Field(sgqlc.types.non_null(DiscountDurationType), graphql_name='durationType')
    type = sgqlc.types.Field(sgqlc.types.non_null(DiscountType), graphql_name='type')
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class SubscriptionPreviewInvoice(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('discount', 'discount_details', 'sub_total', 'tax', 'tax_details', 'total', 'total_excluding_tax')
    discount = sgqlc.types.Field(Money, graphql_name='discount')
    discount_details = sgqlc.types.Field(SubscriptionPreviewDiscount, graphql_name='discountDetails')
    sub_total = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='subTotal')
    tax = sgqlc.types.Field(Money, graphql_name='tax')
    tax_details = sgqlc.types.Field('SubscriptionPreviewTaxDetails', graphql_name='taxDetails')
    total = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='total')
    total_excluding_tax = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='totalExcludingTax')


class SubscriptionPreviewProrations(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('credit', 'debit', 'has_prorations', 'net_amount', 'proration_date')
    credit = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='credit')
    debit = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='debit')
    has_prorations = sgqlc.types.Field(Boolean, graphql_name='hasProrations')
    net_amount = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='netAmount')
    proration_date = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='prorationDate')


class SubscriptionPreviewTaxDetails(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('display_name', 'inclusive', 'percentage')
    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')
    inclusive = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='inclusive')
    percentage = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='percentage')


class SubscriptionPreviewV2(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_period_range', 'has_scheduled_updates', 'immediate_invoice', 'is_plan_downgrade', 'recurring_invoice')
    billing_period_range = sgqlc.types.Field(sgqlc.types.non_null(DateRange), graphql_name='billingPeriodRange')
    has_scheduled_updates = sgqlc.types.Field(Boolean, graphql_name='hasScheduledUpdates')
    immediate_invoice = sgqlc.types.Field(sgqlc.types.non_null(ImmediateSubscriptionPreviewInvoice), graphql_name='immediateInvoice')
    is_plan_downgrade = sgqlc.types.Field(Boolean, graphql_name='isPlanDowngrade')
    recurring_invoice = sgqlc.types.Field(SubscriptionPreviewInvoice, graphql_name='recurringInvoice')


class SubscriptionPrice(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_model', 'created_at', 'feature_id', 'id', 'price', 'subscription', 'updated_at', 'usage_limit')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    price = sgqlc.types.Field(Price, graphql_name='price')
    subscription = sgqlc.types.Field(sgqlc.types.non_null(CustomerSubscription), graphql_name='subscription')
    updated_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class SubscriptionPriceAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_model', 'created_at', 'feature_id', 'id', 'updated_at', 'usage_limit')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    id = sgqlc.types.Field(String, graphql_name='id')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class SubscriptionPriceAvgAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('usage_limit',)
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class SubscriptionPriceCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_model', 'created_at', 'feature_id', 'id', 'updated_at', 'usage_limit')
    billing_model = sgqlc.types.Field(Int, graphql_name='billingModel')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    feature_id = sgqlc.types.Field(Int, graphql_name='featureId')
    id = sgqlc.types.Field(Int, graphql_name='id')
    updated_at = sgqlc.types.Field(Int, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Int, graphql_name='usageLimit')


class SubscriptionPriceEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionPrice), graphql_name='node')


class SubscriptionPriceMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_model', 'created_at', 'feature_id', 'id', 'updated_at', 'usage_limit')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    id = sgqlc.types.Field(String, graphql_name='id')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class SubscriptionPriceMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_model', 'created_at', 'feature_id', 'id', 'updated_at', 'usage_limit')
    billing_model = sgqlc.types.Field(BillingModel, graphql_name='billingModel')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    id = sgqlc.types.Field(String, graphql_name='id')
    updated_at = sgqlc.types.Field(DateTime, graphql_name='updatedAt')
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class SubscriptionPricePreviewDTO(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('discount', 'discount_amount', 'sub_total', 'tax', 'tax_details', 'total', 'total_excluding_tax')
    discount = sgqlc.types.Field(SubscriptionPreviewDiscount, graphql_name='discount')
    discount_amount = sgqlc.types.Field(Money, graphql_name='discountAmount')
    sub_total = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='subTotal')
    tax = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='tax')
    tax_details = sgqlc.types.Field(SubscriptionPreviewTaxDetails, graphql_name='taxDetails')
    total = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='total')
    total_excluding_tax = sgqlc.types.Field(sgqlc.types.non_null(Money), graphql_name='totalExcludingTax')


class SubscriptionPriceSumAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('usage_limit',)
    usage_limit = sgqlc.types.Field(Float, graphql_name='usageLimit')


class SubscriptionPricingTypeStatistics(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('pricing_type', 'total_count')
    pricing_type = sgqlc.types.Field(sgqlc.types.non_null(PricingType), graphql_name='pricingType')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='totalCount')


class SubscriptionScheduledUpdate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('billing_id', 'created_at', 'schedule_status', 'schedule_variables', 'scheduled_execution_time', 'subscription_schedule_type', 'target_package')
    billing_id = sgqlc.types.Field(String, graphql_name='billingId')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    schedule_status = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionScheduleStatus), graphql_name='scheduleStatus')
    schedule_variables = sgqlc.types.Field('ScheduleVariables', graphql_name='scheduleVariables')
    scheduled_execution_time = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='scheduledExecutionTime')
    subscription_schedule_type = sgqlc.types.Field(sgqlc.types.non_null(SubscriptionScheduleType), graphql_name='subscriptionScheduleType')
    target_package = sgqlc.types.Field(PackageDTO, graphql_name='targetPackage')


class SyncState(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('error', 'status', 'vendor_identifier')
    error = sgqlc.types.Field(String, graphql_name='error')
    status = sgqlc.types.Field(sgqlc.types.non_null(SyncStatus), graphql_name='status')
    vendor_identifier = sgqlc.types.Field(sgqlc.types.non_null(VendorIdentifier), graphql_name='vendorIdentifier')


class TestHook(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('test_hook_event_type', 'test_hook_payload')
    test_hook_event_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='testHookEventType')
    test_hook_payload = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='testHookPayload')


class TestHookResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('response_payload', 'response_status_code', 'response_status_text', 'response_success')
    response_payload = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='responsePayload')
    response_status_code = sgqlc.types.Field(Float, graphql_name='responseStatusCode')
    response_status_text = sgqlc.types.Field(String, graphql_name='responseStatusText')
    response_success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='responseSuccess')


class TrialMinDateError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')


class TrialMustBeCancelledImmediately(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'ref_id')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='refId')


class TrialedPlan(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('plan_id', 'plan_ref_id', 'product_id', 'product_ref_id')
    plan_id = sgqlc.types.Field(String, graphql_name='planId')
    plan_ref_id = sgqlc.types.Field(String, graphql_name='planRefId')
    product_id = sgqlc.types.Field(String, graphql_name='productId')
    product_ref_id = sgqlc.types.Field(String, graphql_name='productRefId')


class TriggerSubscriptionMigrationResult(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('task_id',)
    task_id = sgqlc.types.Field(String, graphql_name='taskId')


class TypographyConfiguration(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('body', 'font_family', 'h1', 'h2', 'h3')
    body = sgqlc.types.Field(FontVariant, graphql_name='body')
    font_family = sgqlc.types.Field(String, graphql_name='fontFamily')
    h1 = sgqlc.types.Field(FontVariant, graphql_name='h1')
    h2 = sgqlc.types.Field(FontVariant, graphql_name='h2')
    h3 = sgqlc.types.Field(FontVariant, graphql_name='h3')


class UnPublishedPackageError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'non_published_package_ids', 'package_type')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    non_published_package_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='nonPublishedPackageIds')
    package_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='packageType')


class UncompatibleSubscriptionAddonError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'is_validation_error', 'non_compatible_addons', 'plan_display_name')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    is_validation_error = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValidationError')
    non_compatible_addons = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='nonCompatibleAddons')
    plan_display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='planDisplayName')


class UnitAmountChangeVariables(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('feature_id', 'new_unit_amount')
    feature_id = sgqlc.types.Field(String, graphql_name='featureId')
    new_unit_amount = sgqlc.types.Field(Float, graphql_name='newUnitAmount')


class UnsupportedFeatureTypeError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'feature_type')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    feature_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureType')


class UnsupportedVendorIdentifierError(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('code', 'vendor_identifier')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')
    vendor_identifier = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='vendorIdentifier')


class UpdateEntitlementsOrderDTO(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id', 'order')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    order = sgqlc.types.Field(Float, graphql_name='order')


class UsageEvent(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('customer_id', 'dimensions', 'event_name', 'id', 'resource_id', 'timestamp')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    dimensions = sgqlc.types.Field(JSON, graphql_name='dimensions')
    event_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='eventName')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    timestamp = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='timestamp')


class UsageEventsPreview(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('events',)
    events = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UsageEvent))), graphql_name='events')


class UsageHistory(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('end_date', 'start_date', 'usage_measurements')
    end_date = sgqlc.types.Field(DateTime, graphql_name='endDate')
    start_date = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='startDate')
    usage_measurements = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UsageMeasurementPoint'))), graphql_name='usageMeasurements')


class UsageMeasurement(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'customer', 'customer_id', 'environment', 'environment_id', 'feature', 'feature_id', 'id', 'value')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdAt')
    customer = sgqlc.types.Field(sgqlc.types.non_null(Customer), graphql_name='customer')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment = sgqlc.types.Field(sgqlc.types.non_null(Environment), graphql_name='environment')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature = sgqlc.types.Field(sgqlc.types.non_null(Feature), graphql_name='feature')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class UsageMeasurementAggregateGroupBy(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')


class UsageMeasurementAvgAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(Float, graphql_name='id')


class UsageMeasurementConnection(sgqlc.types.relay.Connection):
    __schema__ = schema
    __field_names__ = ('edges', 'page_info', 'total_count')
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UsageMeasurementEdge'))), graphql_name='edges')
    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')


class UsageMeasurementCountAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id')
    created_at = sgqlc.types.Field(Int, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(Int, graphql_name='environmentId')
    id = sgqlc.types.Field(Int, graphql_name='id')


class UsageMeasurementEdge(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('cursor', 'node')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(ConnectionCursor), graphql_name='cursor')
    node = sgqlc.types.Field(sgqlc.types.non_null(UsageMeasurement), graphql_name='node')


class UsageMeasurementMaxAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')


class UsageMeasurementMinAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'environment_id', 'id')
    created_at = sgqlc.types.Field(DateTime, graphql_name='createdAt')
    environment_id = sgqlc.types.Field(String, graphql_name='environmentId')
    id = sgqlc.types.Field(String, graphql_name='id')


class UsageMeasurementPoint(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('date', 'is_reset_point', 'value')
    date = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='date')
    is_reset_point = sgqlc.types.Field(Boolean, graphql_name='isResetPoint')
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class UsageMeasurementSumAggregate(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(Float, graphql_name='id')


class UsageMeasurementUpdated(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('account_id', 'current_usage', 'customer_id', 'environment_id', 'feature_id', 'next_reset_date', 'resource_id')
    account_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='accountId')
    current_usage = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='currentUsage')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    next_reset_date = sgqlc.types.Field(Float, graphql_name='nextResetDate')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')


class UsageMeasurementWithCurrentUsage(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('created_at', 'current_usage', 'customer_id', 'environment_id', 'feature_id', 'id', 'next_reset_date', 'resource_id', 'timestamp', 'value')
    created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdAt')
    current_usage = sgqlc.types.Field(Float, graphql_name='currentUsage')
    customer_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='customerId')
    environment_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='environmentId')
    feature_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='featureId')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    next_reset_date = sgqlc.types.Field(DateTime, graphql_name='nextResetDate')
    resource_id = sgqlc.types.Field(String, graphql_name='resourceId')
    timestamp = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='timestamp')
    value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='value')


class UsageUpdated(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('entitlement', 'usage')
    entitlement = sgqlc.types.Field(sgqlc.types.non_null(Entitlement), graphql_name='entitlement')
    usage = sgqlc.types.Field(sgqlc.types.non_null(UsageMeasurementUpdated), graphql_name='usage')


class User(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('department', 'email', 'id', 'last_seen_at', 'memberships', 'name', 'profile_image_url')
    department = sgqlc.types.Field(Department, graphql_name='department')
    email = sgqlc.types.Field(String, graphql_name='email')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    last_seen_at = sgqlc.types.Field(DateTime, graphql_name='lastSeenAt')
    memberships = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Member))), graphql_name='memberships')
    name = sgqlc.types.Field(String, graphql_name='name')
    profile_image_url = sgqlc.types.Field(String, graphql_name='profileImageUrl')


class ValidateMergeEnvironment(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('errors', 'is_valid')
    errors = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='errors')
    is_valid = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValid')


class WeeklyResetPeriodConfig(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('weekly_according_to',)
    weekly_according_to = sgqlc.types.Field(WeeklyAccordingTo, graphql_name='weeklyAccordingTo')


class WidgetConfiguration(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('checkout', 'customer_portal', 'paywall')
    checkout = sgqlc.types.Field(CheckoutConfiguration, graphql_name='checkout')
    customer_portal = sgqlc.types.Field(CustomerPortalConfiguration, graphql_name='customerPortal')
    paywall = sgqlc.types.Field(PaywallConfiguration, graphql_name='paywall')


class YearlyResetPeriodConfig(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('yearly_according_to',)
    yearly_according_to = sgqlc.types.Field(YearlyAccordingTo, graphql_name='yearlyAccordingTo')


class ZuoraCredentials(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('base_url', 'client_id', 'client_secret')
    base_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='baseUrl')
    client_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='clientId')
    client_secret = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='clientSecret')


class experimentInfo(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ('group_name', 'group_type', 'id', 'name', 'status')
    group_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='groupName')
    group_type = sgqlc.types.Field(sgqlc.types.non_null(experimentGroupType), graphql_name='groupType')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    status = sgqlc.types.Field(sgqlc.types.non_null(ExperimentStatus), graphql_name='status')



########################################################################
# Unions
########################################################################
class Credentials(sgqlc.types.Union):
    __schema__ = schema
    __types__ = (AwsMarketplaceCredentials, HubspotCredentials, StripeCredentials, ZuoraCredentials)


class ResetPeriodConfiguration(sgqlc.types.Union):
    __schema__ = schema
    __types__ = (MonthlyResetPeriodConfig, WeeklyResetPeriodConfig, YearlyResetPeriodConfig)


class ScheduleVariables(sgqlc.types.Union):
    __schema__ = schema
    __types__ = (AddonChangeVariables, BillingPeriodChangeVariables, DowngradeChangeVariables, UnitAmountChangeVariables)



########################################################################
# Schema Entry Points
########################################################################
schema.query_type = Query
schema.mutation_type = Mutation
schema.subscription_type = Subscription

