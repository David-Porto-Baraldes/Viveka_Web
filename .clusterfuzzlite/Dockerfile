# ClusterFuzzLite Dockerfile (Pinned by SHA-256 for OpenSSF Scorecard 10/10)
FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:502c32425596ef9310bc4b252369c2ef6283ce48926db4586f09aa08bf2455a5
COPY . $SRC/viveka_web
WORKDIR $SRC/viveka_web
COPY .clusterfuzzlite/build.sh $SRC/build.sh
