#! /usr/bin/env python3


from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
import typing
from contextlib import redirect_stdout
from abc import abstractmethod
from pathlib import Path


compiled = set()


def get_generators(p: str) -> list[typing.Callable]:
    """Retrieve generator(s) from the specified .py file.
    Returns a list of functions, each of which outputs a test to stdout (which may be remapped).
    """
    path = Path(p).resolve()
    if path.suffix == '.py':
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ret = [obj for name, obj in vars(module).items() if name.startswith('gen_') and callable(obj)]
        if not ret:
            raise RuntimeError(f'No test generator functions found. Expected at least one function named gen_*.')
        return ret
    elif path.suffix == '.cpp':
        exec_path = path.with_suffix('')
        if path not in compiled:
            subprocess.run(['g++', '-O2', '-o', exec_path, path], check=True)
            print(f'{path} -> {exec_path}')
            compiled.add(path)
        f = lambda: subprocess.run([exec_path], stdout=sys.stdout, check=True)
        f.__name__ = p
        return [f]
    elif path.suffix == '':
        f = lambda: subprocess.run([path], stdout=sys.stdout, check=True)
        f.__name__ = p
        return [f]
    else:
        raise NotImplementedError('Sorry, python is the only supported language for this at the moment!')


def expand_exec(file: Path) -> list:
    """Expand the given executable (e.g. add python before .py files)"""
    if file.suffix == '.py':
        return [sys.executable, file]
    elif file.suffix == '.cpp':
        exec_file = file.with_suffix('')
        if file not in compiled:
            subprocess.run(['g++', '-O2', '-o', exec_file, file], check=True)
            print(f'{file} -> {exec_file}')
            compiled.add(file)
        return [exec_file]
    else:
        return [file]


def run_sol(file: Path, input_file: Path, output_file: Path, force: bool) -> None:
    """Run the solution located at the filename with the input from input_file and write the output to output_file."""
    if output_file.exists() and not force:
        raise RuntimeError(f'Output file {output_file} already exists. Refusing to overwrite without -f.')
    with open(input_file, 'r') as stdin, open(output_file, 'w') as stdout:
        subprocess.run(expand_exec(file.resolve()), stdin=stdin, stdout=stdout, check=True)


def run_checker(file: Path) -> bool:
    """Run the checker. Return True if it returns 0; false otherwise."""
    return subprocess.run(expand_exec(file), check=False).returncode == 0


def token_checker() -> bool:
    """Reads 1.out and 2.out and checks if their tokens are identical."""
    with open('1.out', 'r') as f1, open('2.out', 'r') as f2:
        tokens1 = f1.read().split()
        tokens2 = f2.read().split()
    return tokens1 == tokens2


def print_wa(gen_name: str, trial: int) -> None:
    red = '\033[91m'
    cyan = '\033[96m'
    r = '\033[0m'
    print(f'\n\n{red}-----Wrong answer on test {gen_name}:{trial}-----{r}')
    print(f'{cyan}Input (gen.in):{r}')
    with open('gen.in', 'r') as f:
        print(f.read())
    print(f'{cyan}Output from solution 1 (1.out):{r}')
    with open('1.out', 'r') as f:
        print(f.read())
    print(f'{cyan}Output from solution 2 (2.out):{r}')
    with open('2.out', 'r') as f:
        print(f.read())


def main():
    parser = argparse.ArgumentParser(description='gtest, a stresstesting tool for competitive programming')
    parser.add_argument('-s', '--sol1', type=str, required=True, help='Path to the (first) solution')
    parser.add_argument('-t', '--sol2', type=str, default=None, help='Path to the (second) solution (optional)')
    parser.add_argument('-g', '--generator', type=str, required=True, help='Path to the test generator (.py)')
    parser.add_argument('-c', '--checker', type=str, default=None, help='Path to the checker (executable, .py, or .cpp) (optional) - checker should read 1.out and 2.out')
    parser.add_argument('-T', '--trials', type=int, default=10000, help='Number of trials to run')
    parser.add_argument('-f', action='store_true', default=False, help='Allow overwriting of existing gen.in, 1.out, and 2.out files')
    args = parser.parse_args()
    if args.sol2 is None and args.checker is None:
        raise RuntimeError('The default token checker requires two solutions to compare.')

    genfile = Path('gen.in')
    if genfile.exists() and not args.f:
        raise RuntimeError(f'Input file {genfile} already exists. Refusing to overwrite without -f.')
    gens = get_generators(args.generator)
    for gen in gens:
        for t in range(1, args.trials+1):
            with open(genfile, 'w') as f:
                with redirect_stdout(f):
                    gen()
            run_sol(Path(args.sol1), genfile, Path('1.out'), args.f)
            if args.sol2 is not None:
                run_sol(Path(args.sol2), genfile, Path('2.out'), args.f)
            if args.checker:
                result = run_checker(Path(args.checker))
            else:
                result = token_checker()
            if not result:
                print_wa(gen.__name__, t)
                return
            print(f'\r{gen.__name__}  {t}/{args.trials}', end='')
        print()
    print('\nAll tests passed!')


if __name__ == '__main__':
    main()
