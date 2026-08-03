def main() -> int:
    import opticargo_shared

    print({"shared": getattr(opticargo_shared, "__name__", "opticargo_shared")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
