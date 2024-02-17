from sigma.processing.transformations import AddConditionTransformation, FieldMappingTransformation, DetectionItemFailureTransformation, RuleFailureTransformation, SetStateTransformation, ChangeLogsourceTransformation
from sigma.processing.conditions import LogsourceCondition, IncludeFieldCondition, ExcludeFieldCondition, RuleProcessingItemAppliedCondition
from sigma.processing.pipeline import ProcessingItem, ProcessingPipeline
from sigma.rule import SigmaDetectionItem
from sigma.exceptions import SigmaTransformationError

class InvalidFieldTransformation(DetectionItemFailureTransformation):
    """
    Overrides the apply_detection_item() method from DetectionItemFailureTransformation to also include the field name
    in the error message
    """

    def apply_detection_item(self, detection_item: SigmaDetectionItem) -> None:
        field_name = detection_item.field
        self.message = f"Invalid SigmaDetectionItem field name encountered: {field_name}. " + self.message
        raise SigmaTransformationError(self.message)

def CarbonBlackResponse_pipeline() -> ProcessingPipeline:
    os_filters = [
        # Windows
        ProcessingItem(
            identifier="cbr_windows_os",
            transformation=AddConditionTransformation({
                "os_type": "windows"
            }),
            rule_conditions=[
                LogsourceCondition(product="windows")
            ]
        ),
        # Linux
        ProcessingItem(
            identifier="cbr_linux_os",
            transformation=AddConditionTransformation({
                "os_type": "linux"
            }),
            rule_conditions=[
                LogsourceCondition(product="linux")
            ]
        ),
        # macOS
        ProcessingItem(
            identifier="cbr_macos_os",
            transformation=AddConditionTransformation({
                "os_type": "osx"
            }),
            rule_conditions=[
                LogsourceCondition(product="macos")
            ]
        )
    ]

    translation_dict = {
        "ProcessId":"process_pid",
        "Image":"process_name",
        "ImagePath":"path",
        "Description":"file_desc",
        "Product":"product_name",
        "Company":"company_name",
        "CommandLine":"cmdline",
        "CurrentDirectory":"process_name",
        "User":"username",
        "md5":"md5",
        "sha256":"sha256",
        "ParentProcessId":"parent_pid",
        "ParentImage":"parent_name",
        "TargetFilename":"filemod", 
        "ImageLoaded":"modload",
        "TargetObject": "regmod",
        "DestinationHostname":"domain",
        "DestinationPort":"ipport",
        "DestinationIp":"ipaddr",
        "SourceIp":"ipaddr",
        "SourcePort":"ipport",
        "dst_ip":"ipaddr",
        "src_ip":"ipaddr",
        "dst_port":"ipport",
        "src_port":"ipport"
    }

    field_mappings = [
        ProcessingItem(
            identifier="cbr_fieldmapping",
            transformation=FieldMappingTransformation(translation_dict),
            rule_condition_linking=any,
            rule_conditions=[
                LogsourceCondition(category="process_creation"),
                LogsourceCondition(category="file_change"),
                LogsourceCondition(category="file_rename"),
                LogsourceCondition(category="file_delete"),
                LogsourceCondition(category="file_event"),
                LogsourceCondition(category="registry_add"),
                LogsourceCondition(category="registry_delete"),
                LogsourceCondition(category="registry_event"),
                LogsourceCondition(category="registry_set"),
                LogsourceCondition(category="network_connection"),
                LogsourceCondition(category="firewall")
            ]
        ),
    ]

    change_logsource_info = [
        # Add service to be CarbonBlackResponse for pretty much everything
        ProcessingItem(
            identifier="cbr_logsource",
            transformation=ChangeLogsourceTransformation(
                service="carbonblackresponse"
            ),
            rule_condition_linking=any,
            rule_conditions=[
                LogsourceCondition(category="process_creation"),
                LogsourceCondition(category="file_change"),
                LogsourceCondition(category="file_rename"),
                LogsourceCondition(category="file_delete"),
                LogsourceCondition(category="file_event"),
                LogsourceCondition(category="image_load"),
                LogsourceCondition(category="registry_add"),
                LogsourceCondition(category="registry_delete"),
                LogsourceCondition(category="registry_event"),
                LogsourceCondition(category="registry_set"),
                LogsourceCondition(category="network_connection"),
                LogsourceCondition(category="firewall")
            ]
        ),
    ]

    unsupported_rule_types = [
        # Show error if unsupported option
        ProcessingItem(
            identifier="cbr_fail_rule_not_supported",
            rule_condition_linking=any,
            transformation=RuleFailureTransformation("Rule type not yet supported by the Carbon Black Response Sigma backend"),
            rule_condition_negation=True,
            rule_conditions=[
                RuleProcessingItemAppliedCondition("cbr_logsource")
            ]
        )
    ]

    unsupported_field_names = [
        ProcessingItem(
            identifier="cbr_fail_field_name_not_supported",
            transformation=InvalidFieldTransformation("The supported fields are: {" + 
                "}, {".join(sorted(list(translation_dict.keys()))) + '}'),
            field_name_conditions=[
                ExcludeFieldCondition(fields=list(translation_dict.keys()))
            ],
            field_name_condition_linking=any
        )
    ]

    return ProcessingPipeline(
        name="carbonblack response pipeline",
        allowed_backends=frozenset(),                                               # Set of identifiers of backends (from the backends mapping) that are allowed to use this processing pipeline. This can be used by frontends like Sigma CLI to warn the user about inappropriate usage.
        priority=50,            # The priority defines the order pipelines are applied. See documentation for common values.
        items=[
            *unsupported_field_names,
            *os_filters,
            *field_mappings,
            *change_logsource_info,
            *unsupported_rule_types
        ]
    )

def CarbonBlack_pipeline() -> ProcessingPipeline:

    supported_categories = [
        LogsourceCondition(category="process_creation"),
        LogsourceCondition(category="file_change"),
        LogsourceCondition(category="file_rename"),
        LogsourceCondition(category="file_delete"),
        LogsourceCondition(category="file_event"),
        LogsourceCondition(category="registry_add"),
        LogsourceCondition(category="registry_delete"),
        LogsourceCondition(category="registry_event"),
        LogsourceCondition(category="registry_set"),
        LogsourceCondition(category="network_connection"),
        LogsourceCondition(category="firewall")
    ]

    general_supported_fields = ['md5','sha256']

    translation_dict = {
        "ProcessId":"process_pid",
        "Image":"process_name",
        "Description":"process_file_description",
        "Product":"process_product_name",
        "Company":"process_company_name",
        "CommandLine":"process_cmdline",
        "CurrentDirectory":"process_name",
        "User":"process_username",
        "IntegrityLevel":"process_integrity_level",
        "ParentProcessId":"parent_pid",
        "ParentImage":"parent_name",
        "ParentCommandLine":"parent_cmdline",
        "OriginalFileName":"process_original_filename",
        "TargetFilename":"filemod_name", 
        "ImageLoaded":"modload_name",
        "Signature":"modload_publisher",
        "TargetObject": "regmod_name",
        "DestinationHostname":"netconn_domain",
        "DestinationPort":"netconn_port",
        "DestinationIp":["netconn_ipv4","netconn_ipv6"],
        "SourceIp":["netconn_ipv4","netconn_ipv6"],
        "SourcePort":"netconn_port",
        "Protocol":["netconn_protocol", "netconn_application_protocol"],
        "dst_ip":["netconn_ipv4","netconn_ipv6"],
        "src_ip":["netconn_ipv4","netconn_ipv6"],
        "dst_port":"netconn_port",
        "src_port":"netconn_port",
        "DstPort":"netconn_port",
        "SrcPort":"netconn_port"
    }

    os_filters = [
        # Windows
        ProcessingItem(
            identifier="cb_windows_os",
            transformation=AddConditionTransformation({
                "device_os": "WINDOWS"
            }),
            rule_conditions=[
                LogsourceCondition(product="windows")
            ]
        ),
        # Linux
        ProcessingItem(
            identifier="cb_linux_os",
            transformation=AddConditionTransformation({
                "device_os": "LINUX"
            }),
            rule_conditions=[
                LogsourceCondition(product="linux")
            ]
        ),
        # macOS
        ProcessingItem(
            identifier="cb_macos_os",
            transformation=AddConditionTransformation({
                "device_os": "MAC"
            }),
            rule_conditions=[
                LogsourceCondition(product="macos")
            ]
        )
    ]

    field_mappings = [
        ProcessingItem(
            identifier="cb_fieldmapping",
            transformation=FieldMappingTransformation(translation_dict),
            rule_condition_linking=any,
            rule_conditions=supported_categories
        ),
        # Process Creation Hashes
        ProcessingItem(
            identifier="cb_process_creation_fieldmapping",
            transformation=FieldMappingTransformation({
                "md5":"process_hash",
                "sha256":"process_hash",
            }),
            rule_conditions=[
                LogsourceCondition(category="process_creation"),
            ]
        ),
        # Module Load Hashes
        ProcessingItem(
            identifier="cb_image_load_fieldmapping",
            transformation=FieldMappingTransformation({
                "sha256":"modload_hash",
                "md5": "modload_hash",
            }),
            rule_conditions=[
                LogsourceCondition(category="image_load")
            ]
        ),
        # File Changes Hashes
        ProcessingItem(
            identifier="cb_filemod_fieldmapping",
            transformation=FieldMappingTransformation({
                "sha256":"filemod_hash",
                "md5": "filemod_hash",
            }),
            rule_condition_linking=any,
            rule_conditions=[
                LogsourceCondition(category="file_change"),
                LogsourceCondition(category="file_rename"),
                LogsourceCondition(category="file_delete"),
                LogsourceCondition(category="file_event"),
            ]
        ),
    ]

    change_logsource_info = [
        # Add service to be CarbonBlack for pretty much everything
        ProcessingItem(
            identifier="cb_logsource",
            transformation=ChangeLogsourceTransformation(
                service="carbonblack"
            ),
            rule_condition_linking=any,
            rule_conditions=[
                LogsourceCondition(category="process_creation"),
                LogsourceCondition(category="file_change"),
                LogsourceCondition(category="file_rename"),
                LogsourceCondition(category="file_delete"),
                LogsourceCondition(category="file_event"),
                LogsourceCondition(category="image_load"),
                LogsourceCondition(category="registry_add"),
                LogsourceCondition(category="registry_delete"),
                LogsourceCondition(category="registry_event"),
                LogsourceCondition(category="registry_set"),
                LogsourceCondition(category="network_connection"),
                LogsourceCondition(category="firewall")
            ]
        ),
    ]

    unsupported_rule_types = [
        # Show error if unsupported option
        ProcessingItem(
            identifier="cb_fail_rule_not_supported",
            rule_condition_linking=any,
            transformation=RuleFailureTransformation("Rule type not yet supported by the Carbon Black Sigma backend"),
            rule_condition_negation=True,
            rule_conditions=[
                RuleProcessingItemAppliedCondition("cb_logsource")
            ]
        )
    ]

    unsupported_field_names = [
        ProcessingItem(
            identifier="cb_fail_field_name_not_supported",
            transformation=InvalidFieldTransformation("The supported fields are: {" + 
                "}, {".join(sorted(list(translation_dict.keys()) + general_supported_fields)) + '}'),
            field_name_conditions=[
                ExcludeFieldCondition(fields=list(translation_dict.keys()) + general_supported_fields)
            ],
            field_name_condition_linking=any
        )
    ]

    return ProcessingPipeline(
        name="carbonblack pipeline",
        allowed_backends=frozenset(), # Set of identifiers of backends (from the backends mapping) that are allowed to use this processing pipeline. This can be used by frontends like Sigma CLI to warn the user about inappropriate usage.
        priority=50, # The priority defines the order pipelines are applied. See documentation for common values.
        items=[
            *unsupported_field_names,
            *os_filters,
            *field_mappings,
            *change_logsource_info,
            *unsupported_rule_types
        ]
    )