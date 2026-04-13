# import time
#
# import typer
# from rich.console import Console
#
# console = Console()
# print = console.print
#
# app = typer.Typer(name="fourier-grx", no_args_is_help=True, pretty_exceptions_enable=False)
#
#
# @app.command()
# def run(
#         config: str = typer.Argument(help="Path to the config file"),
#         namespace: str = typer.Option(None, help="Namespace for the robot"),
#         freq: int = typer.Option(400, help="Main loop frequency in hz. defaults to 400hz."),
#         verbose: bool = typer.Option(False, help="Print internal debug info"),
#         visualize: bool = typer.Option(False, help="Visualize the robot in meshcat"),
# ):
#     """Run the robot server."""
#
#     robot = RobotServer(config, namespace=namespace, freq=freq, visualize=visualize, verbose=verbose)
#
#
# @app.command()
# def calibrate(
#         namespace: str = typer.Option(None, help="Namespace for the robot"),
#         ip: str = typer.Option("localhost", help="IP address of the robot server."),
#         # output_path: str = typer.Argument(default="sensor_offsets.json", help="Path to the output file"),
# ):
#     """Calibrate the robot sensors and save the offsets to a file"""
#     try:
#         client = RobotClient(namespace=namespace, server_ip=ip)
#         client.calibrate_sensors()
#         client.close()
#     except Exception as e:
#         print(e)
#
#
# # @app.command()
# # def generate_sensor_offset():
# #     """Generate sensor offset file from the control SDK installed on the host machine, usually located at ~/RoCS/bin/pythonscripts/absAngle.json"""
# #     from fourier_grx.tools.load_sensor_offset import load_sensor_offset
#
# #     load_sensor_offset()
#
#
# @app.command()
# def disable(
#         namespace: str = typer.Option(None, help="Namespace for the robot"),
#         ip: str = typer.Option("localhost", help="IP address of the robot server."),
# ):
#     """Disable all the motors."""
#     try:
#         client = RobotClient(namespace=namespace, server_ip=ip)
#         time.sleep(0.1)
#         client.set_enable(False)
#         time.sleep(0.1)
#         client.close()
#     except Exception as e:
#         print(e)
#
#
# @app.command()
# def enable(
#         namespace: str = typer.Option(None, help="Namespace for the robot"),
#         ip: str = typer.Option("localhost", help="IP address of the robot server."),
# ):
#     """Enable all the motors."""
#     try:
#         client = RobotClient(namespace=namespace, server_ip=ip)
#         time.sleep(0.1)
#         client.set_enable(True)
#         time.sleep(0.1)
#         client.close()
#     except Exception as e:
#         print(e)
#
#
# @app.command()
# def states(
#         namespace: str = typer.Option(None, help="Namespace for the robot"),
#         ip: str = typer.Option("localhost", help="IP address of the robot server."),
# ):
#     """Print the current robot states."""
#     import time
#
#     import numpy as np
#     from rich.table import Table
#
#     try:
#         client = RobotClient(namespace=namespace, server_ip=ip)
#         time.sleep(0.1)
#         table = Table("Type", "Data", title="Current :robot: states (in radians )")
#         for sensor_type, sensor_data in client._states.items():
#             for sensor_name, sensor_reading in sensor_data.items():
#                 sensor_value = (
#                     str(np.round(np.deg2rad(sensor_reading), 3))
#                     if (sensor_type == "joint" or sensor_type == "velocity") and sensor_name in ["position", "velocity"]
#                     else str(np.round(sensor_reading, 3))
#                 )
#                 table.add_row(
#                     sensor_type + "/" + sensor_name,
#                     sensor_value,
#                 )
#         print(table)
#
#         client.close()
#     except Exception as e:
#         print(e)
#
#
# if __name__ == "__main__":
#     app()
