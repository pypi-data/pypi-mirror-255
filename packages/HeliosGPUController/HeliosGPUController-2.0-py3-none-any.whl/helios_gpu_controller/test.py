from time import sleep

from src.helios_gpu_controller.HeliosGPUController import HeliosGPUController

if __name__ == '__main__':
    gpu_controller = HeliosGPUController(config_file="conf.yaml")

    gpu_controller.throttle_gpu()

    #gpu_controller.stop_helios()
