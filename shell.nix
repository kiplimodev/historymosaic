
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3.pkgs.beautifulsoup4
    pkgs.python3.pkgs.openai
    pkgs.python3.pkgs.python-dotenv
    pkgs.python3.pkgs.pytest
    pkgs.python3.pkgs.requests
  ];
}
