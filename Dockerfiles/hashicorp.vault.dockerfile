FROM hashicorp/vault as vault

RUN apk add --no-cache curl

ENV VAULT_DEV_ROOT_TOKEN_ID=root
ENV VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
ENV VAULT_DEV_TLS_DISABLE=true

EXPOSE 8200

ENTRYPOINT ["vault", "server", "-dev"]