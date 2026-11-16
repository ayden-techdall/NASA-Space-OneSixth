"""Run both models and write outputs/results_v2.json and outputs/curves_v2.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import one_sixth_model as m1
import physics_model as m2

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(root, "outputs"), exist_ok=True)
r1, c1 = m1.run()
r2, c2 = m2.run()
results = {"model_1_empirical_cellulose": r1, "model_2_physics": r2}
curves = {"model_1": c1, "model_2": c2}
json.dump(results, open(os.path.join(root, "outputs/results_v2.json"), "w"), indent=2)
json.dump(curves, open(os.path.join(root, "outputs/curves_v2.json"), "w"))
print(json.dumps(r2, indent=1))
