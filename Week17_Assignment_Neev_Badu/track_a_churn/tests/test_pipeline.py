from src.common import features, load_telco
from src.train import CONFIGS, build_pipeline


def test_dataset_and_three_genuine_configurations():
    frame = load_telco()
    assert len(frame) > 7000
    assert set(frame["Churn"].unique()) == {0, 1}
    assert len(CONFIGS) == 3
    assert len({tuple(sorted(c.items())) for c in CONFIGS}) == 3


def test_pipeline_fits_small_sample():
    X, y = features(load_telco())
    model = build_pipeline(X, CONFIGS[0]).fit(X.head(250), y.head(250))
    assert len(model.predict(X.head(5))) == 5
