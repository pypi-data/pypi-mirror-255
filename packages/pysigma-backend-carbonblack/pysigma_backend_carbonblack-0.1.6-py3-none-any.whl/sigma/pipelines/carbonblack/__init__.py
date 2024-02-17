from .carbonblack import CarbonBlack_pipeline, CarbonBlackResponse_pipeline
# TODO: add all pipelines that should be exposed to the user of your backend in the import statement above.

pipelines = {
    "carbonblack_pipeline": CarbonBlack_pipeline,
    "carbonblackresponse_pipeline": CarbonBlackResponse_pipeline
}