Colony Picking Demo
===================

Demo for Arc colony picking submission.
User upload sample_submission.csv
Then barcodes are generated. These barcodes will be fed to the Qpix.
The Qpix gives an output which is parsed by the colony picking submission script
Output is a heatmap color coded by plate number


# Development

## Installation

### Conda env

```bash
mamba env create -f colony_picking_demo.yml
mamba activate colony_picking_demo
```

## Run

```bash
streamlit run colony_picking_app.py --server.port=8080 --server.address=0.0.0.0
```


## Deployment

### Docker

Build the container:

```bash
# set env vars
IMG_NAME=colony-picking-demo
IMG_VERSION=0.1.0
# build (run from base-dir of repo)
docker build --platform linux/amd64 -t ${IMG_NAME}:${IMG_VERSION} .
```

Test run the app:

```bash
PORT=8080
docker run -it --rm \
  -p ${PORT}:${PORT} \
  --platform linux/amd64 \
  --env PORT=${PORT} \
  ${IMG_NAME}:${IMG_VERSION}
```

> include `--entrypoint /bin/bash` for an interative test run of the container

```bash
PORT=8080
docker run -it --rm \
  -p ${PORT}:${PORT} \
  --platform linux/amd64 \
  --env PORT=${PORT} \
  --entrypoint /bin/bash \
  ${IMG_NAME}:${IMG_VERSION}
```

## GCP Service Account

Activate an appropriate GCP service account for the subsequent steps:

```bash
gcloud auth activate-service-account --key-file=/Users/nickyoungblut/.gcp/arc-gec-nlpp-2b111543a8a0.json
```

You can obtain a service account key (JSON) file from the GCP console (IAM & Admin => Service Accounts => Select account => Create Key).

## Artifact Registry

If needed, create Artifact Registry:

```bash
DESCRIPTION="Colony-picking-demo app container"
gcloud artifacts repositories create ${IMG_NAME} \
  --repository-format=docker \
  --project=arc-gec-nlpp \
  --location=us-west1 \
  --description="${DESCRIPTION}" \
  --async
```

Push to Artifact Registry:

```bash
docker tag ${IMG_NAME}:${IMG_VERSION} \
  us-west1-docker.pkg.dev/arc-gec-nlpp/${IMG_NAME}/${IMG_NAME}:${IMG_VERSION} \
  && docker push us-west1-docker.pkg.dev/arc-gec-nlpp/${IMG_NAME}/${IMG_NAME}:${IMG_VERSION}
```

## GCP Cloud Run

Deploy to Cloud Run:

```bash
# deploy to Cloud Run 
gcloud run deploy ${IMG_NAME} \
  --service-account=809958227570-compute@developer.gserviceaccount.com \
  --image=us-west1-docker.pkg.dev/arc-gec-nlpp/${IMG_NAME}/${IMG_NAME}:${IMG_VERSION} \
  --region=us-west1 \
  --project=arc-gec-nlpp \
  --cpu=2 \
  --memory=3Gi \
  --max-instances=1 \
  --concurrency=80 \
  --allow-unauthenticated \
  && gcloud run services update-traffic ${IMG_NAME} --to-latest
```

# Troubleshooting

## Authorization

Activate a service account:

```bash
gcloud auth activate-service-account --key-file=/Users/nickyoungblut/.gcp/arc-gec-nlpp-2b111543a8a0.json
```

To activate your personal:

```bash
gcloud auth list
gcloud config set account <YOUR_PERSONAL_ACCOUNT>
```