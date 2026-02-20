from pathlib import Path

from app.services.model_service import train_and_save_model


if __name__ == "__main__":
    output = Path(__file__).resolve().parent / "models" / "catboost_disease.cbm"
    train_and_save_model(output)
    print(f"Model saved to: {output}")
