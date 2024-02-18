env_template = """
# AWS LOCAL
# ------------------------------------------------------------------------------
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_STORAGE_BUCKET_NAME=
S3_REGION_NAME=
CDN_URL=https://base-cdn.advantch.com
S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com/base
S3_CUSTOM_DOMAIN=base-cdn.advantch.com


# site
SITE_URL=http://localhost:8000

# Multitenancy
# ------------------------------------------------------------------------------
TENANT_MODE = 3

# Redis
# ------------------------------------------------------------------------------
REDIS_URL=redis://redis:6379/0


# Stripe
# ------------------------------------------------------------------------------
STRIPE_TEST_SECRET_KEY=sk_test_
STRIPE_TEST_PUBLIC_KEY=pk_test_
DJSTRIPE_WEBHOOK_SECRET=whsec_


# PostgreSQL
# ------------------------------------------------------------------------------
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
"""
