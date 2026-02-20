import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.nlp_service import BiomedicalNLPService
from app.services.model_service import DiseaseModelService
from app.services.explainability import IntegratedGradientsExplainer
from app.services.risk_engine import RiskAwareLayer
from app.services.diet_engine import NutrientScoredLayer


@pytest.fixture
def nlp_service():
    return BiomedicalNLPService()


@pytest.fixture
def model_service():
    service = DiseaseModelService()
    if not service._is_fitted:
        from app.services.model_service import train_and_save_model
        model_path = Path(__file__).parent.parent / "models" / "catboost_disease.cbm"
        train_and_save_model(model_path)
        service._load_if_exists()
    return service


@pytest.fixture
def explainer():
    return IntegratedGradientsExplainer()


@pytest.fixture
def risk_layer():
    return RiskAwareLayer()


@pytest.fixture
def diet_layer():
    return NutrientScoredLayer()
