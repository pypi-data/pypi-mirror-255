{{- define "dyff.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}


{{- define "dyff.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}


{{- define "dyff.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/* api helpers */}}

{{- define "dyff.api.fullname" -}}
{{ include "dyff.fullname" . }}-api
{{- end }}

{{- define "dyff.api.name" -}}
{{ include "dyff.name" . }}-api
{{- end }}

{{- define "dyff.api.labels" -}}
helm.sh/chart: {{ include "dyff.chart" . }}
{{ include "dyff.api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "dyff.api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dyff.name" . }}-api
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "dyff.api.serviceAccountName" -}}
{{- if .Values.api.serviceAccount.create }}
{{- default (include "dyff.api.fullname" .) .Values.api.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.api.serviceAccount.name }}
{{- end }}
{{- end }}


{{/* orchestrator helpers */}}

{{- define "dyff.orchestrator.fullname" -}}
{{ include "dyff.fullname" . }}-orchestrator
{{- end }}

{{- define "dyff.orchestrator.name" -}}
{{ include "dyff.name" . }}-orchestrator
{{- end }}

{{- define "dyff.orchestrator.labels" -}}
helm.sh/chart: {{ include "dyff.chart" . }}
{{ include "dyff.orchestrator.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "dyff.orchestrator.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dyff.name" . }}-orchestrator
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "dyff.orchestrator.serviceAccountName" -}}
{{- if .Values.orchestrator.serviceAccount.create }}
{{- default (include "dyff.orchestrator.fullname" .) .Values.orchestrator.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.orchestrator.serviceAccount.name }}
{{- end }}
{{- end }}


{{/* orchestrator-db helpers */}}

{{- define "dyff.orchestrator.db.fullname" -}}
{{ include "dyff.orchestrator.fullname" . }}-db
{{- end }}

{{- define "dyff.orchestrator.db.labels" -}}
helm.sh/chart: {{ include "dyff.chart" . }}
{{ include "dyff.orchestrator.db.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "dyff.orchestrator.db.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dyff.orchestrator.name" . }}-db
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
