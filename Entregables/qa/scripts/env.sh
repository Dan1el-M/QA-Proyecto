#!/usr/bin/env bash
# Resolve the moved runtime from this script, independent of the caller's directory.
_qa_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -f "$_qa_root/.qa-runtime/rubyinstaller-4.0.5-1-x64/bin/ruby.exe" ]] && { ! command -v ruby >/dev/null 2>&1 || [[ "${QA_USE_PORTABLE_RUBY:-0}" == 1 ]]; }; then
  export PATH="$_qa_root/.qa-runtime/rubyinstaller-4.0.5-1-x64/bin:$_qa_root/.qa-runtime/gems/bin:$PATH"
  export GEM_HOME="$(cygpath -w "$_qa_root/.qa-runtime/gems")"
  _qa_msys="$(cygpath -u "$USERPROFILE")/AppData/Local/Temp/qa-mundial-msys64"
  [[ -f "$_qa_msys/usr/bin/sh.exe" ]] && export MSYS2_PATH="$(cygpath -w "$_qa_msys")"
  unset _qa_msys
fi
export RI_FORCE_PATH_FOR_DLL=1
export RAILS_ENV=test
if command -v cygpath >/dev/null 2>&1; then
  export BUNDLE_GEMFILE="$(cygpath -w "$_qa_root/qa/Gemfile")"
else
  export BUNDLE_GEMFILE="$_qa_root/qa/Gemfile"
fi
unset _qa_root
export QA_URL=http://127.0.0.1:3100
if ! command -v python >/dev/null 2>&1; then
  _qa_profile="$(cygpath -u "$USERPROFILE")"
  _qa_python="$_qa_profile/.cache/codex-runtimes/codex-primary-runtime/dependencies/python"
  [[ -f "$_qa_python/python.exe" ]] && export PATH="$_qa_python:$PATH"
  unset _qa_python _qa_profile
fi
