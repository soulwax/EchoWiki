# 7. Extension Patterns

This page turns the architecture into practical patterns. Use it when adding a capability.

## Pattern: Add A Data-Driven Gameplay Value

```mermaid
flowchart TD
    value[New gameplay value]
    toml[Add field to Assets/Data/*.toml]
    serde[Add serde field and default in src/data]
    apply[Apply in pure game or runtime owner]
    test[Add focused test if pure]
    modcheck[Validate in mod_check if cross-referenced]
    docs[Document in Docs/MODDING.md]

    value --> toml --> serde --> apply --> test --> modcheck --> docs
```

Keep numeric balance values out of runtime actor constructors when practical.

## Pattern: Add A Runtime Visual

```mermaid
flowchart TD
    visual[New runtime visual]
    asset{Needs asset/shader?}
    manifest[Reference from data/manifest]
    fallback[Provide fallback rendering]
    runtime[Draw/apply in src/runtime]
    pack[Verify asset_pack discovery]
    smoke[cargo run smoke test]

    visual --> asset
    asset -- yes --> manifest --> fallback --> runtime
    asset -- no --> runtime
    runtime --> pack --> smoke
```

A missing shader or texture should not crash the game.

## Pattern: Add A Lua-Visible Action

```mermaid
flowchart LR
    action[New action]
    command[Add or reuse GameCommand]
    lua[Expose Lua helper]
    runtime[Apply command in runtime]
    validate[mod_check command validation]
    docs[Docs/MODDING.md]

    action --> command --> lua --> runtime --> validate --> docs
```

Prefer shared `GameCommand` verbs over direct Lua mutation.

## Pattern: Add A Tool Diagnostic

```mermaid
flowchart TD
    bad[Bad content state]
    detect[Detect in src/bin/mod_check.rs or relevant tool]
    message[Human-readable warning/error]
    refs[Show file/id/location]
    test[Unit test parser/validator helper]

    bad --> detect --> message --> refs --> test
```

Good diagnostics tell a content author what to fix, not just that parsing failed.

## Pattern: Add A Choreography Beat

```mermaid
flowchart TB
    beat[New beat]
    schema[Serde model and schema]
    engine[Pure engine intent/command]
    runtime[Runtime apply layer]
    cli[choreo validate/preview]
    docs[Modding docs]

    beat --> schema --> engine --> runtime --> cli --> docs
```

If it is authored scene behavior, route it through choreography.

## Pattern: Add A New Asset Type

```mermaid
flowchart TD
    assettype[New asset type]
    location[Choose source directory]
    owner[Choose manifest owner if possible]
    discovery[Update discovery only if needed]
    verify[asset_pack --dry-run --list]
    modcheck[mod_check if references can break]
    release[release pack verify]

    assettype --> location --> owner --> discovery --> verify --> modcheck --> release
```

The preferred outcome is no `asset_pack.rs` edit because an existing scanned directory or manifest already owns the file.

## Pattern: Extract Pure Logic From Runtime

```mermaid
flowchart LR
    runtime[Runtime code]
    identify[Identify deterministic rule]
    pure[Move rule to src/game or src/ui]
    adapter[Keep Macroquad adapter in runtime]
    tests[Add pure tests]

    runtime --> identify --> pure --> adapter --> tests
```

Do this when runtime code is becoming hard to test, but avoid broad rewrites. Extract the smallest stable rule.

## Review Checklist

Before calling an architectural change done:

- Does it preserve the runtime vs pure-module boundary?
- Is the modding story clear?
- Are missing files or malformed data handled gracefully?
- Does release packaging include required assets?
- Is there a focused verification command?
- Did the contributor docs or modding docs need an update?
