-- Forensic Triage & Postmortem Intelligence — Supabase schema
-- Apply with: psql $SUPABASE_DB_URL -f schema.sql

create extension if not exists "uuid-ossp";

-- ============================ users ============================
create type forensic_role as enum ('INVESTIGATOR', 'ANALYST', 'ADMIN');

create table if not exists users (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  password_hash text not null,
  role forensic_role not null,
  name text,
  created_at timestamptz default now()
);

-- ============================ cases ============================
create type case_status as enum ('INTAKE', 'IN_TRIAGE', 'REVIEW', 'CLOSED');
create type risk_level as enum ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

create table if not exists cases (
  id text primary key,
  title text not null,
  status case_status not null default 'INTAKE',
  risk_score int default 0,
  risk_level risk_level default 'LOW',
  created_by uuid references users(id),
  analyst_id uuid references users(id),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_cases_risk on cases(risk_level, risk_score desc);

-- ============================ evidence_files ============================
create table if not exists evidence_files (
  id uuid primary key default uuid_generate_v4(),
  case_id text references cases(id) on delete cascade,
  file_type text not null,
  storage_url text not null,
  ocr_text text,
  upload_by uuid references users(id),
  created_at timestamptz default now()
);

-- ============================ autopsy ============================
create table if not exists autopsy_reports (
  id uuid primary key default uuid_generate_v4(),
  case_id text references cases(id) on delete cascade,
  evidence_file_id uuid references evidence_files(id),
  cause_of_death text,
  manner_of_death text,
  injuries jsonb,
  toxicology jsonb,
  postmortem_indicators jsonb,
  overall_confidence numeric(4, 3),
  gemini_cached_response jsonb,
  created_at timestamptz default now()
);

-- ============================ logs ============================
create table if not exists cctv_logs (
  id uuid primary key default uuid_generate_v4(),
  case_id text references cases(id) on delete cascade,
  camera_id text not null,
  location text,
  event_timestamp timestamptz not null,
  event_type text,
  attributes jsonb default '{}'
);
create index if not exists idx_cctv_case_ts on cctv_logs(case_id, event_timestamp);

create table if not exists gps_logs (
  id uuid primary key default uuid_generate_v4(),
  case_id text references cases(id) on delete cascade,
  subject_id text not null,
  timestamp timestamptz not null,
  latitude double precision not null,
  longitude double precision not null,
  accuracy_m numeric(8, 2),
  source text
);
create index if not exists idx_gps_case_ts on gps_logs(case_id, timestamp);

create table if not exists call_logs (
  id uuid primary key default uuid_generate_v4(),
  case_id text references cases(id) on delete cascade,
  subject_id text not null,
  timestamp timestamptz not null,
  duration_sec int,
  cell_tower_id text,
  call_type text
);
create index if not exists idx_call_case_ts on call_logs(case_id, timestamp);

-- ============================ contradictions ============================
create type contradiction_type as enum ('IMPOSSIBLE', 'SUSPICIOUS', 'UNVERIFIABLE');
create type investigative_priority as enum ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

create table if not exists contradictions (
  id uuid primary key default uuid_generate_v4(),
  case_id text references cases(id) on delete cascade,
  type contradiction_type not null,
  source_a jsonb not null,
  source_b jsonb not null,
  time_delta_min numeric(10, 2),
  distance_km numeric(10, 3),
  severity contradiction_type not null,
  explanation text,
  investigative_priority investigative_priority,
  created_at timestamptz default now()
);

-- ============================ AI provenance ============================
create table if not exists ai_results (
  id uuid primary key default uuid_generate_v4(),
  case_id text references cases(id) on delete cascade,
  module text not null,
  input_hash text not null,
  output jsonb not null,
  model_version text not null,
  cached boolean default false,
  created_at timestamptz default now(),
  unique(input_hash, model_version)
);
create index if not exists idx_ai_case_module on ai_results(case_id, module);

-- ============================ audit ============================
create table if not exists audit_logs (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references users(id),
  action text not null,
  entity_type text not null,
  entity_id text,
  metadata jsonb default '{}',
  created_at timestamptz default now()
);
create index if not exists idx_audit_user on audit_logs(user_id, created_at desc);

-- ============================ sign-off ============================
create table if not exists report_signoffs (
  id uuid primary key default uuid_generate_v4(),
  case_id text references cases(id) on delete cascade,
  analyst_id uuid references users(id),
  signed_at timestamptz default now(),
  disputed_findings jsonb default '[]',
  unique(case_id)
);
