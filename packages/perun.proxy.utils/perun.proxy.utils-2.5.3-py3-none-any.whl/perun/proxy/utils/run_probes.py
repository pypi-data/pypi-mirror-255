#!/usr/bin/python3
import re
import subprocess
import sys
from threading import Thread

import yaml


def open_file(filepath):
    try:
        with open(filepath) as f:
            return f.read()
    except OSError as e:
        print(
            f"Cannot open config with path: {filepath}, error: {e.strerror}",
            file=sys.stderr,
        )
        sys.exit(2)


def get_metrics_and_new_output(output):
    """
    Parses metrics from output, metrics must be in one of (or combination of)
    the following formats:
        1) |metric1=val;val;;;|metric2=val (delimiter |)
        2) |metric1=val;metric2=val2; (delimiter ;)
        3) |metric1=val metric2=val2 (delimiter ' ')

        Values must be int or float
    """
    metrics_pattern = r"(\s\|\s|\|)(\w+=[\d.;]+(;|\s|$))+"

    match = re.search(metrics_pattern, output)
    if match:
        output = re.sub(metrics_pattern, " ", output)
        metrics = re.sub(r"\s", "", match.group())
        metrics = re.sub(r"^\|", "", metrics)
        metrics = re.sub(r"(\d;?)([a-zA-Z])", r"\1|\2", metrics)
        return metrics.strip(), output.strip()
    return None, output


def run_probe(probe_name, command):
    """
    Runs nagios monitoring probe and prints output in following formats:
        1) return_code probe_name metrics output
        2) return_code probe_name - output

    metrics output format:
        metric1=val;|metric2=val2|metric3=val3;val3;;;|metric4=val4
    """
    result = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output = re.sub("[ \t\n]+", " ", result.stdout)
    search = re.search(r" - .*", output)
    if search:
        output = re.sub(r"^ - ", "", search.group())
    metrics, new_output = get_metrics_and_new_output(output)
    if metrics:
        print(f"{result.returncode} {probe_name} {metrics} {new_output}")
    else:
        print(f"{result.returncode} {probe_name} - {output}")
    return result.returncode


def main():
    config_filepath = "/etc/run_probes_cfg.yaml"
    config = yaml.safe_load(open_file(config_filepath))
    if not config:
        return

    for _, options in config.items():
        module = options["module"]
        for name, args in options.get("runs").items():
            command = ["python3", "-m", module]
            if args is not None:
                for arg_name, arg_val in args.items():
                    if len(arg_name) == 1:
                        arg_name = "-" + arg_name
                    else:
                        arg_name = "--" + arg_name
                    if arg_val is True:
                        arg_val = "true"
                    elif arg_val is False:
                        arg_val = "false"
                    command.append(arg_name)
                    if arg_val is not None:
                        command.append(str(arg_val))
            Thread(target=run_probe, args=[name, command]).start()


if __name__ == "__main__":
    main()
