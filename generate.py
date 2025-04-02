import re
import subprocess


def system(command):
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True)
    return result.stdout.strip()


def get_arch_list():
    # Get the list of targets from rustc
    targets_output = subprocess.run(
        ["rustc", "+nightly", "--print=target-list"],
        capture_output=True, text=True, check=True
    ).stdout.strip()
    targets = targets_output.splitlines()

    archs = set()
    for target in targets:
        cfg_output = subprocess.run(
            ["rustc", "+nightly", "--print=cfg", f"--target={target}"],
            capture_output=True, text=True, check=True
        ).stdout.splitlines()

        for cfg in cfg_output:
            match = re.search(r'target_arch="([^"]+)"', cfg)
            if match:
                archs.add(match.group(1))

    return sorted(archs)


arch_list = get_arch_list()

arch_list.sort()
print(arch_list)


# upper rules have higher priority
cache_size_regex = {
    256: [
        "^s390x.*"
    ],
    128: [
        "^mips64.*",  # it is up to 128 bytes but 32 is more common
        "^arm64.*",
        "^powerpc.*",
        "^aarch64.*",
        "^x86_64.*",
        "^wasm.*",  # most common for modern cpus supporting wasm is 128
        "^amdgpu.*",
        "^nvptx64.*",
    ],
    64: [
        "^sparc64.*",
        "^bpf.*",
        "^csky.*",
        "^loongarch64.*",
        "^x86.*",
    ],
    32: [
        "^mips.*",
        "^hexagon.*",
        "^sparc.*",
        "^arm.*",
        "^avr.*",
        "^xtensa.*",
        "^riscv.*",
    ],
    16: [
        "^m68k.*"
    ],
    8: [
        "^msp430.*"
    ]
}


def get_cache_size(arch):
    for size, regex_list in cache_size_regex.items():
        for regex in regex_list:
            if re.match(regex, arch):
                return size
    print(f"Warning: No cache size rule found for {arch}, defaulting to 64")
    return 64


groups = {}
for arch in arch_list:
    size = get_cache_size(arch)
    if size not in groups:
        groups[size] = []
    groups[size].append(arch)


header = """#![no_std]
// for target_archs that are nightly only
#![allow(unexpected_cfgs)] 
use core::{fmt, ops::Deref, ops::DerefMut};
#[derive(Clone, Copy, Default, Hash, PartialEq, Eq)]"""


footer = """// CacheGuard is primarily used to pad atomic variables to prevent cache
// invalidation that can occur due to atomic operations. By aligning memory
// according to the target architecture's cache size rules, CacheGuard mitigates
// false sharing and enhances performance, particularly in concurrent
// environments.
pub struct CacheGuard<T> {
    inner: T,
}
/// Creates a new `CacheGuard` instance that wraps the provided value.
///
/// This function is a constructor for `CacheGuard`. It takes ownership of the
/// input value and returns a new `CacheGuard` instance containing that value.
///
/// # Examples
///
/// ```rust
/// use cacheguard::CacheGuard;
/// use core::sync::atomic::AtomicUsize;
/// let cache_guard = CacheGuard::new(AtomicUsize::new(0));
/// ```
///
/// # Parameters
///
/// - `inner`: The value to be wrapped within the `CacheGuard`.
impl<T> CacheGuard<T> {
    pub const fn new(inner: T) -> CacheGuard<T> {
        CacheGuard::<T> { inner }
    }
    pub fn into_inner(self) -> T {
        self.inner
    }
}
impl<T: fmt::Debug> fmt::Debug for CacheGuard<T> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("CacheGuard")
            .field("inner", &self.inner)
            .finish()
    }
}
impl<T: fmt::Display> fmt::Display for CacheGuard<T> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        fmt::Display::fmt(&self.inner, f)
    }
}
impl<T> From<T> for CacheGuard<T> {
    fn from(t: T) -> CacheGuard<T> {
        CacheGuard::new(t)
    }
}
impl<T> Deref for CacheGuard<T> {
    type Target = T;
    fn deref(&self) -> &T {
        &self.inner
    }
}
impl<T> DerefMut for CacheGuard<T> {
    fn deref_mut(&mut self) -> &mut T {
        &mut self.inner
    }
}
unsafe impl<T: Send> Send for CacheGuard<T> {}
unsafe impl<T: Sync> Sync for CacheGuard<T> {}
"""

file = open("src/lib.rs", "w")
file.write(header + "\n")


sorted_group_keys = sorted(list(groups.keys()))
default_size = 64

all_but_default_archs = []
print(sorted_group_keys)
for size in sorted_group_keys:
    archs = groups[size]
    if size == default_size:
        continue
    if len(archs) > 1:
        file.write(f"#[cfg_attr(any(\n")
        for arch in archs:
            file.write(f"    target_arch = \"{arch}\",\n")
        file.write(f"), repr(align({size})))]\n")
    else:
        file.write(f"#[cfg_attr(target_arch = \"{archs[0]}\"")
        file.write(f", repr(align({size})))]\n")
    all_but_default_archs.extend(groups[size])


all_but_default_archs.sort()
including_list = ", ".join(groups[default_size])
file.write(
    f"// Defaults to {default_size}-byte alignment for targets such as {including_list} and all the others\n")
file.write(f"#[cfg_attr(not(any(\n")
for arch in all_but_default_archs:
    file.write(f"    target_arch = \"{arch}\",\n")
file.write(")), repr(align({})))]\n".format(default_size))

file.write(footer)
file.close()

system("cargo +nightly fmt")
system("cargo +nightly clippy --fix --allow-dirty")
