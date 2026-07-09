import os
import socket
import sys
import xmlrpc.client


RPC_URL = "http://localhost:1080/RPC2"
RPC_HOST = "localhost"
RPC_PORT = 1080

MODELS = [
    ("step_01_three_phase_bridge", "step_01_three_phase_bridge"),
    ("step_02_six_step_table", "step_02_six_step_table"),
    ("step_03_open_loop_commutation", "step_03_open_loop_commutation"),
    ("step_04_hall_commutation", "step_04_hall_commutation"),
    ("step_05_pwm_duty", "step_05_pwm_duty"),
    ("step_06_speed_estimation", "step_06_speed_estimation"),
    ("step_07_speed_pi", "step_07_speed_pi"),
    ("step_08_plecs_full_model", "step_08_plecs_full_model"),
]


def model_path(root, directory, model_name):
    return os.path.join(root, directory, model_name + ".plecs")


def main():
    socket.setdefaulttimeout(5)
    root = os.path.dirname(os.path.abspath(__file__))

    try:
        with socket.create_connection((RPC_HOST, RPC_PORT), timeout=2):
            pass
    except OSError as exc:
        print(f"PLECS_RPC_NOT_READY {RPC_HOST}:{RPC_PORT}: {exc}", flush=True)
        return 2

    server = xmlrpc.client.ServerProxy(RPC_URL, allow_none=True)
    output_times = [i * 0.01 for i in range(0, 21)]
    sim_opts = {"SolverOpts": {"OutputTimes": output_times}}
    failed = False

    for directory, model_name in MODELS:
        path = model_path(root, directory, model_name)

        if not os.path.exists(path):
            print(f"MISSING {path}", flush=True)
            failed = True
            continue

        try:
            print(f"SIM_START {model_name}", flush=True)
            server.plecs.load(path)
            server.plecs.simulate(model_name, sim_opts)
            print(f"SIM_OK {model_name}", flush=True)
        except Exception as exc:
            print(f"SIM_FAILED {model_name}: {exc}", flush=True)
            failed = True
        finally:
            try:
                server.plecs.close(model_name)
            except Exception:
                pass

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
