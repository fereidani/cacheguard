# CacheGuard

** A lightweight cache guard that pads atomics to prevent false sharing in concurrent Rust systems **

[![Crates.io][crates-badge]][crates-url]
[![Documentation][doc-badge]][doc-url]
[![MIT licensed][mit-badge]][mit-url]

[crates-badge]: https://img.shields.io/crates/v/cacheguard.svg?style=for-the-badge
[crates-url]: https://crates.io/crates/cacheguard
[mit-badge]: https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge
[mit-url]: https://github.com/fereidani/cacheguard/blob/master/LICENSE
[doc-badge]: https://img.shields.io/docsrs/cacheguard?style=for-the-badge
[doc-url]: https://docs.rs/cacheguard

CacheGuard is primarily used to pad atomic variables to prevent cache invalidation that can occur due to atomic operations. By aligning memory according to the target architecture's cache size rules, `CacheGuard` mitigates false sharing and enhances performance, particularly in concurrent environments.

## Difference with Crossbeam CachePadded

While both `CacheGuard` and Crossbeam `CachePadded` aim to mitigate cache invalidation issues, there are key differences:

- `CacheGuard` is a standalone crate designed specifically for padding atomic types, whereas Crossbeam `CachePadded` is a part of the broader crossbeam-utils ecosystem.
- `CacheGuard` is tuned for worst-case and not most common scenarios and also supports a wider range of platforms.
- `CacheGuard` uses a code generation approach to dynamically read rustc target platforms, which simplifies maintenance and allows for tailored library code generation.
- This design makes `CacheGuard` more specialized and easier to maintain as it directly targets the needs of preventing cache invalidation in concurrent environments.

## Usage

Add `CacheGuard` to your `Cargo.toml`:

```toml
[dependencies]
cacheguard = "0.1"
```

Wrap your atomic pointers with `CacheGuard` to ensure proper memory alignment. For example, you can create a struct that holds two atomic pointers wrapped in `CacheGuard` as follows:

```rust
use cacheguard::CacheGuard;
use std::sync::atomic::{AtomicUsize, Ordering};

struct ConcurrentStructure {
    counter1: CacheGuard<AtomicUsize>,
    counter2: CacheGuard<AtomicUsize>,
}
```

This example demonstrates wrapping two atomic counters within a struct using CacheGuard.

## License

This project is licensed under the MIT License.
