from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from audit.router import router as audit_router
from auth.router import router as auth_router
from config import get_settings
from modules.admin.router import router as admin_router
from modules.autopsy.router import router as autopsy_router
from modules.call.router import router as call_router
from modules.cases.router import router as cases_router
from modules.cctv.router import router as cctv_router
from modules.correlation.router import router as correlation_router
from modules.disputes.router import router as disputes_router
from modules.evidence.router import router as evidence_router
from modules.ingest.router import router as ingest_router
from modules.risk.router import router as risk_router
from modules.signoff.router import router as signoff_router
from modules.tod.router import router as tod_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Forensic Triage & Postmortem Intelligence",
        description="AI-assisted forensic triage. Deterministic engines + FIPL prompt layer.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(cases_router, prefix="/api/cases", tags=["cases"])
    app.include_router(ingest_router, prefix="/api/cases", tags=["ingest"])
    app.include_router(evidence_router, prefix="/api/evidence", tags=["evidence"])
    app.include_router(autopsy_router, prefix="/api/autopsy", tags=["autopsy"])
    app.include_router(cctv_router, prefix="/api/cctv", tags=["cctv"])
    app.include_router(call_router, prefix="/api/call", tags=["call"])
    app.include_router(correlation_router, prefix="/api/correlation", tags=["correlation"])
    app.include_router(risk_router, prefix="/api/risk", tags=["risk"])
    app.include_router(tod_router, prefix="/api/tod", tags=["tod"])
    app.include_router(signoff_router, prefix="/api/signoff", tags=["signoff"])
    app.include_router(disputes_router, prefix="/api/disputes", tags=["disputes"])
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
    app.include_router(audit_router, prefix="/api/audit", tags=["audit"])

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    s = get_settings()
    uvicorn.run("main:app", host=s.api_host, port=s.api_port, reload=True)
