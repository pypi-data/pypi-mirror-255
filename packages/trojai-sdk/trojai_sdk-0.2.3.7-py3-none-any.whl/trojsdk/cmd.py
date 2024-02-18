from trojsdk.core import client_utils
from python_hosts import Hosts, HostsEntry
import webbrowser
import sys
from trojsdk.core.client_utils import TrojJobHandler


def run(args):
    import subprocess

    with subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    ) as process:
        for line in process.stdout:
            print(line.decode("utf8"), end="")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="trojsdk", description="Troj sdk command line utils"
    )
    parser.add_argument(
        "-config", metavar="-c", type=str, help="Path to the config file"
    )
    parser.add_argument(
        "-art_config",
        metavar="-artc",
        type=str,
        help="Path to the auto-redteaming config file",
    )
    parser.add_argument(
        "-cybersec_config",
        metavar="-cybersec",
        type=str,
        help="Path to the cyber-security config file",
    )
    parser.add_argument(
        "-query_mongo",
        metavar="-qm",
        help="Pass an arbitrary dict to query the mongodb",
    )
    parser.add_argument(
        "-endpoint", metavar="-e", help="The end point where your cluster is located"
    )
    parser.add_argument(
        "-dl_fails",
        action="store_true",
        help="Choose a test run from the completed pods and pass the job name to get all failed samples in a csv",
    )
    parser.add_argument(
        "-job_name",
        metavar="-jn",
        help="Choose a test run from the completed pods and pass the job name to get all failed samples in a csv",
    )
    parser.add_argument("-save_path", metavar="-sp", help="path to save failed output")
    parser.add_argument(
        "-auth_config",
        metavar="-ac",
        help="Pass an auth config to doanload test run details",
    )
    parser.add_argument(
        "-test", action="store_true", help="Run tests with TrojAI supplied configs."
    )
    parser.add_argument("-gp", action="store_true", help="Get pods")
    parser.add_argument("-gpw", action="store_true", help="Get pods watch")
    parser.add_argument("-nossl", action="store_true", help="No ssl flag")
    parser.add_argument(
        "-minio",
        nargs="?",
        const="127.0.0.1",
        metavar="IP ADDRESS",
        type=str,
        help=argparse.SUPPRESS,
        # help="Install the host entry and open the MinIO dashboard for the local cluster. Default value of 127.0.0.1.",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.gp:
        import subprocess

        # open kubectl get pods -n=trojai
        process = run(["kubectl", "get", "pods", "-n=trojai"])

    if args.gpw:
        # open kubectl get pods -n=trojai -w
        try:
            process = run(["kubectl", "get", "pods", "-n=trojai", "-w"])
        except KeyboardInterrupt:
            print("Exiting watch...")

    if args.config:
        client_utils.submit_evaluation(path_to_config=args.config, nossl=args.nossl)
    if args.art_config:
        client_utils.submit_autoredteaming(
            path_to_config=args.art_config, nossl=args.nossl
        )

    if args.cybersec_config:
        client_utils.submit_cybersec(
            path_to_config=args.cybersec_config, nossl=args.nossl
        )

    if args.dl_fails:
        if args.job_name:
            if args.auth_config:
                import json
                from trojsdk.core.experiment_tools import TrojExperimenter

                print("Loading auth")
                conf = TrojExperimenter(args.auth_config)
                tjh = TrojJobHandler()
                tjh.create_client(conf)
                print("Extracting run for job name: " + args.job_name)
                troj_output_obj = tjh.extract_run(args.job_name)
                print("Gathering failed samples for all attacks")
                failed_samples_dict = troj_output_obj.return_failed_samples()
                # Serializing json
                json_object = json.dumps(failed_samples_dict, indent=4)
                print("Saving output")
                if args.save_path:
                    # Writing to sample.json
                    with open(args.save_path, "w") as outfile:
                        outfile.write(json_object)
                    print("Output saved to path: " + args.save_path)
                else:
                    print("Saving to current directory under default name")
                    with open(
                        "./" + args.job_name + "-failed-samples.json", "w"
                    ) as outfile:
                        outfile.write(json_object)
                    print(
                        "Output saved to path: "
                        + "./"
                        + args.job_name
                        + "-failed-samples.json"
                    )

            else:
                print(
                    "No auth config supplied, please pass a link to a valid trojai auth config json"
                )

    if args.minio:
        address = args.minio
        name = "trojai.minio"
        comment = "Trojai MinIO host"

        hosts = Hosts()
        hosts.remove_all_matching(comment=comment)

        try:
            host_entry = HostsEntry(
                entry_type="ipv4", address=address, names=[name], comment=comment
            )
        except Exception as e:
            try:
                host_entry = HostsEntry(
                    entry_type="ipv6", address=address, names=[name], comment=comment
                )
            except Exception as e2:
                raise e from e2

        hosts.add([host_entry])
        hosts.write()
        webbrowser.open_new_tab("http://" + name)


if __name__ == "__main__":
    main()
