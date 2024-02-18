FROM golang:1.20 as builder
ARG TARGETOS
ARG TARGETARCH

WORKDIR /workspace

COPY go.mod go.sum ./
RUN go mod download

COPY main.go ./
COPY agent/ agent/

# confluent kafka package requires C libraries
RUN CGO_ENABLED=1 GOOS=${TARGETOS:-linux} GOARCH=${TARGETARCH} go build -a -o workflows-informer main.go

# https://github.com/GoogleContainerTools/distroless
# 'base' is required because we need libc
# '-debian12' is required to get latest glibc; '-debian11' causes:
# /workflows-informer: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32' not found (required by /workflows-informer)
# /workflows-informer: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.34' not found (required by /workflows-informer)
# See: https://github.com/GoogleContainerTools/distroless/issues/1342
FROM gcr.io/distroless/base-debian12:nonroot
WORKDIR /
COPY --from=builder /workspace/workflows-informer .
USER 65532:65532

ENTRYPOINT ["/workflows-informer"]
