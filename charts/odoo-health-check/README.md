# odoo-health-check

Run [odoo-health-check](https://github.com/Jaikin-SASU/odoo-health-check) on a schedule against a public Odoo instance. The chart installs a Kubernetes `CronJob` that audits what a visitor or a search engine already sees:

- **Indexability**: `Disallow: /` in robots.txt, `noindex` meta tag, `X-Robots-Tag` header. A frequent cause of an Odoo website missing from Google is a domain name set in *Website > Configuration* while another host serves the same database.
- **Database manager**: whether `/web/database/manager` is publicly reachable.
- **HTTPS and HSTS**.
- **Security headers**: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.
- **Odoo version** (read from the asset path) and **sitemap.xml**.

The audit only sends `GET` requests on public paths. It never authenticates, so no Odoo database name or credential is needed. Audit only instances you own or are explicitly authorised to test.

## Install

```console
helm repo add jaikin https://jaikin-sasu.github.io/odoo-health-check
helm repo update
helm install odoo-audit jaikin/odoo-health-check \
  --set target.url=https://example.odoo.com
```

Or straight from the source tree:

```console
git clone https://github.com/Jaikin-SASU/odoo-health-check
helm install odoo-audit ./odoo-health-check/charts/odoo-health-check \
  --set target.url=https://example.odoo.com
```

Run the audit once, right now, and read the report (it is written in French):

```console
kubectl create job --from=cronjob/odoo-audit-odoo-health-check odoo-audit-now
kubectl logs job/odoo-audit-now
```

## Reading the result

| Exit code | Meaning | Job status |
|---|---|---|
| `0` | No failure | Complete |
| `1` | At least one check failed (or a warning, with `audit.strict=true`) | Failed |
| `2` | The target is unreachable | Failed |

A failed Job is kept by `failedJobsHistoryLimit` and is not retried (`backoffLimit: 0`), so a regular alert on failed Jobs is enough to be warned when an instance becomes invisible to search engines.

## Keep the URL in a Secret

If the address of the instance should not appear in the release values, store it in an existing Secret:

```console
kubectl create secret generic odoo-target --from-literal=url=https://example.odoo.com
helm install odoo-audit jaikin/odoo-health-check \
  --set target.urlFromSecret.name=odoo-target
```

## Values

| Key | Default | Description |
|---|---|---|
| `target.url` | `""` | Public URL of the instance to audit. Required unless `target.urlFromSecret.name` is set |
| `target.urlFromSecret.name` | `""` | Existing Secret holding the URL (takes precedence over `target.url`) |
| `target.urlFromSecret.key` | `url` | Key of the URL in that Secret |
| `audit.timeout` | `15` | Network timeout in seconds |
| `audit.strict` | `false` | Fail on warnings too |
| `audit.insecure` | `false` | Do not verify the TLS certificate of the target |
| `audit.json` | `false` | Print the report as JSON |
| `schedule` | `"0 6 * * 1"` | Cron schedule (every Monday at 06:00) |
| `timeZone` | `""` | IANA time zone of the schedule (Kubernetes 1.27+) |
| `suspend` | `false` | Suspend the CronJob |
| `concurrencyPolicy` | `Forbid` | CronJob concurrency policy |
| `successfulJobsHistoryLimit` / `failedJobsHistoryLimit` | `3` / `3` | Jobs kept |
| `backoffLimit` | `0` | Retries of a failed audit |
| `activeDeadlineSeconds` | `300` | Maximum duration of one audit |
| `image.repository` | `quay.io/jaikin/odoo-health-check` | Container image |
| `image.tag` | `""` | Image tag (defaults to the chart `appVersion`) |
| `image.pullPolicy` | `IfNotPresent` | Image pull policy |
| `imagePullSecrets` | `[]` | Pull secrets |
| `podSecurityContext` / `securityContext` | non-root (UID 10001), read-only root file system, all capabilities dropped | Security contexts |
| `resources` | 10m CPU / 32Mi request, 128Mi limit | Container resources |
| `nodeSelector`, `tolerations`, `affinity` | empty | Scheduling |
| `podLabels`, `podAnnotations` | empty | Extra pod metadata |
| `nameOverride`, `fullnameOverride` | `""` | Name overrides |

## Uninstall

```console
helm uninstall odoo-audit
```

## About

The tool and this chart are released under the MIT licence. Source: [github.com/Jaikin-SASU/odoo-health-check](https://github.com/Jaikin-SASU/odoo-health-check).

Built by [JAIKIN](https://www.jaikin.eu/integrateur-odoo-france), Odoo integration and AI agents for SMEs.
