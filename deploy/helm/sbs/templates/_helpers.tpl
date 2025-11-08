{{- define "sbs.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "sbs.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "sbs.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "sbs.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "sbs.selectorLabels" -}}
app.kubernetes.io/name: {{ include "sbs.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "sbs.image" -}}
{{- $registry := .repository -}}
{{- $tag := default .tag "latest" -}}
{{- printf "%s:%s" $registry $tag -}}
{{- end -}}

{{- define "sbs.postgresql.host" -}}
{{- $override := index .Values "postgresql" "fullnameOverride" | default "" -}}
{{- if $override -}}
{{- $override -}}
{{- else -}}
{{- printf "%s-postgresql" .Release.Name -}}
{{- end -}}
{{- end -}}

{{- define "sbs.redis.host" -}}
{{- $override := index .Values "redis" "fullnameOverride" | default "" -}}
{{- if $override -}}
{{- $override -}}
{{- else -}}
{{- printf "%s-redis" .Release.Name -}}
{{- end -}}
{{- end -}}

{{- define "sbs.temporal.host" -}}
{{- $override := index .Values "temporal" "fullnameOverride" | default "" -}}
{{- if $override -}}
{{- $override -}}
{{- else -}}
{{- printf "%s-temporal" .Release.Name -}}
{{- end -}}
{{- end -}}

{{- define "sbs.nats.host" -}}
{{- $override := index .Values "nats" "fullnameOverride" | default "" -}}
{{- if $override -}}
{{- $override -}}
{{- else -}}
{{- printf "%s-nats" .Release.Name -}}
{{- end -}}
{{- end -}}

