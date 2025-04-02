#![no_std]
// for target_archs that are nightly only
#![allow(unexpected_cfgs)]
use core::{fmt, ops::Deref, ops::DerefMut};
#[derive(Clone, Copy, Default, Hash, PartialEq, Eq)]
#[cfg_attr(target_arch = "msp430", repr(align(8)))]
#[cfg_attr(target_arch = "m68k", repr(align(16)))]
#[cfg_attr(
    any(
        target_arch = "arm",
        target_arch = "avr",
        target_arch = "hexagon",
        target_arch = "mips",
        target_arch = "mips32r6",
        target_arch = "riscv32",
        target_arch = "riscv64",
        target_arch = "sparc",
        target_arch = "xtensa",
    ),
    repr(align(32))
)]
#[cfg_attr(
    any(
        target_arch = "aarch64",
        target_arch = "amdgpu",
        target_arch = "arm64ec",
        target_arch = "mips64",
        target_arch = "mips64r6",
        target_arch = "nvptx64",
        target_arch = "powerpc",
        target_arch = "powerpc64",
        target_arch = "wasm32",
        target_arch = "wasm64",
        target_arch = "x86_64",
    ),
    repr(align(128))
)]
#[cfg_attr(target_arch = "s390x", repr(align(256)))]
// Defaults to 64-byte alignment for targets such as bpf, csky, loongarch64, sparc64, x86 and all
// the others
#[cfg_attr(
    not(any(
        target_arch = "aarch64",
        target_arch = "amdgpu",
        target_arch = "arm",
        target_arch = "arm64ec",
        target_arch = "avr",
        target_arch = "hexagon",
        target_arch = "m68k",
        target_arch = "mips",
        target_arch = "mips32r6",
        target_arch = "mips64",
        target_arch = "mips64r6",
        target_arch = "msp430",
        target_arch = "nvptx64",
        target_arch = "powerpc",
        target_arch = "powerpc64",
        target_arch = "riscv32",
        target_arch = "riscv64",
        target_arch = "s390x",
        target_arch = "sparc",
        target_arch = "wasm32",
        target_arch = "wasm64",
        target_arch = "x86_64",
        target_arch = "xtensa",
    )),
    repr(align(64))
)]
// CacheGuard is primarily used to pad atomic variables to prevent cache
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
