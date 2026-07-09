import os
import sys
import time
import xmlrpc.client


MODEL_NAME = "bldc_six_step_learning"
MODEL_FILE = os.path.join(os.getcwd(), MODEL_NAME + ".plecs")
RPC_URL = "http://localhost:1080/RPC2"


def main():
    if not os.path.exists(MODEL_FILE):
        print(f"MODEL_FILE_NOT_FOUND: {MODEL_FILE}", file=sys.stderr)
        return 2

    server = xmlrpc.client.ServerProxy(RPC_URL, allow_none=True)

    try:
        server.plecs.load(MODEL_FILE)
    except Exception as exc:
        print(f"LOAD_FAILED: {exc}", file=sys.stderr)
        return 3

    output_times = [i * 0.001 for i in range(0, 301)]
    sim_opts = {"SolverOpts": {"OutputTimes": output_times}}

    try:
        result = server.plecs.simulate(MODEL_NAME, sim_opts)
    except Exception as exc:
        print(f"SIM_FAILED: {exc}", file=sys.stderr)
        try:
            server.plecs.close(MODEL_NAME)
        except Exception:
            pass
        return 4

    try:
        server.plecs.close(MODEL_NAME)
    except Exception:
        pass

    print(f"SIM_OK model={MODEL_NAME}")
    times = result.get("Time", [])
    values = result.get("Values", [])
    print(f"samples={len(times)} signals={len(values)}")
    if times:
        print(f"t_start={times[0]:.6g} t_end={times[-1]:.6g}")
    else:
        print("returned_scope_samples=0")

    for idx, signal in enumerate(values[:4], start=1):
        if signal:
            print(
                f"sig{idx}: first={signal[0]:.6g} "
                f"last={signal[-1]:.6g} min={min(signal):.6g} max={max(signal):.6g}"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
