# msir-infer
Inference Server for msir, following InferenceProtocalV2 with additional custom apis designed for images

## usage
### buf curl
```
buf curl --data '{"model_name": "ocr", "image_url": "http://im.png"}' --schema ./msir-infer/proto/apis/inference/v1/infer.proto -v http://localhost:9002/inference.v1.ImageInferenceService/InferImage
```

### grpcurl
```
grpcurl -plaintext -d '{"model_name": "ocr", "image_url": "http://someimage.png"}' -import-path ./msir-infer/proto -proto ./msir-infer/proto/apis/inference/v1/infer.proto localhost:9002 inference.v1.ImageInferenceService/InferImage
```