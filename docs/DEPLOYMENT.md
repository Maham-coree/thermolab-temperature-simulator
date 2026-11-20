# Streamlit Community Cloud Deployment

ThermoLab's Streamlit frontend runs the existing mathematical engine directly in the app process. It does not depend on a backend hosted at `localhost:8000`, and no `API_URL` secret or external API service is required.

## Deploy the Streamlit app

1. Push the project to a GitHub repository accessible to Streamlit Community Cloud.
2. In Community Cloud, create an app from that repository and select the branch containing the project.
3. Set **Main file path** to `app.py` at the repository root.
4. Deploy. Community Cloud installs the packages listed in `requirements.txt`.

No Streamlit secrets are required for the current application.

## Runtime architecture

- The frontend validates simulation and comparison inputs with the shared Pydantic request models.
- It calls `backend.math_engine.simulate` for each requested simulation.
- The FastAPI application remains available for local development and API testing. Run it from the project root with:

  ```powershell
  uvicorn backend.main:app --reload
  ```

  Its interactive API documentation is available at `http://127.0.0.1:8000/docs`.

The Community Cloud frontend does not start or expose this local FastAPI server. If a separate remote API is introduced later, it will need its own deployment and an explicit, securely configured integration.
