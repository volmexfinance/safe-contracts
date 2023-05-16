methods {
    function getThreshold() external returns (uint256) envfree;
    function disableModule(address,address) external;
    function nonce() external returns (uint256) envfree;
    function getOwners() external returns (address[] memory) envfree;

    // harnessed
    function getModule(address) external returns (address) envfree;
    function getOwner(address) external returns (address) envfree;
    function isOwner(address) external returns (bool) envfree;
    function getOwnerCount() external returns (uint256) envfree;

    // optional
    function execTransactionFromModuleReturnData(address,uint256,bytes,SafeHarness.Operation) external returns (bool, bytes memory);
    function execTransactionFromModule(address,uint256,bytes,SafeHarness.Operation) external returns (bool);
    function execTransaction(address,uint256,bytes,SafeHarness.Operation,uint256,uint256,uint256,address,address,bytes) external returns (bool);
}

definition noHavoc(method f) returns bool =
    f.selector != sig:execTransactionFromModuleReturnData(address,uint256,bytes,SafeHarness.Operation).selector
    && f.selector != sig:execTransactionFromModule(address,uint256,bytes,SafeHarness.Operation).selector 
    && f.selector != sig:execTransaction(address,uint256,bytes,SafeHarness.Operation,uint256,uint256,uint256,address,address,bytes).selector;

definition reachableOnly(method f) returns bool =
    f.selector != sig:setup(address[],uint256,address,bytes,address,address,uint256,address).selector
    && f.selector != sig:simulateAndRevert(address,bytes).selector;

/// Nonce must never decrease
rule nonceMonotonicity(method f) filtered {
    f -> noHavoc(f) && reachableOnly(f)
} {
    uint256 nonceBefore = nonce();

    calldataarg args; env e;
    f(e, args);

    uint256 nonceAfter = nonce();

    assert nonceAfter == nonceBefore || to_mathint(nonceAfter) == nonceBefore + 1;
}


/// The module sentinel must never point to the zero address.
/// @notice It should either point to itself or some nonzero value
invariant liveModuleSentinel()
    getModule(1) != 0
    filtered { f -> noHavoc(f) && reachableOnly(f) }
    { preserved {
        requireInvariant noModuleDeadEnds(getModule(1), 1);
    }}

/// Threshold must always be nonzero.
invariant nonzeroThreshold()
    getThreshold() > 0
    filtered { f -> noHavoc(f) && reachableOnly(f) }

/// Two different modules must not point to the same module
invariant uniqueModulePrevs(address prev1, address prev2)
    prev1 != prev2 && getModule(prev1) != 0 => getModule(prev1) != getModule(prev2)
    filtered { f -> noHavoc(f) && reachableOnly(f) }
    { 
        preserved {
            requireInvariant noModuleDeadEnds(getModule(prev1), prev1);
            requireInvariant noModuleDeadEnds(getModule(prev2), prev2);
            requireInvariant uniqueModulePrevs(prev1, 1);
            requireInvariant uniqueModulePrevs(prev2, 1);
            requireInvariant uniqueModulePrevs(prev1, getModule(prev2));
            requireInvariant uniqueModulePrevs(prev2, getModule(prev1));
        }
    }

/// A module that points to the zero address must not have another module pointing to it.
invariant noModuleDeadEnds(address dead, address lost)
    dead != 0 && getModule(dead) == 0 => getModule(lost) != dead
    filtered { f -> noHavoc(f) && reachableOnly(f) }
    {
        preserved {
            requireInvariant liveModuleSentinel();
            requireInvariant noModuleDeadEnds(getModule(1), 1);
        }
        preserved disableModule(address prevModule, address module) with (env e) {
            requireInvariant uniqueModulePrevs(prevModule, lost);
            requireInvariant uniqueModulePrevs(prevModule, dead);
            requireInvariant noModuleDeadEnds(dead, module);
            requireInvariant noModuleDeadEnds(module, dead);
        }
    }


/// The owner sentinel must never point to the zero address.
/// @notice It should either point to itself or some nonzero value
invariant liveOwnerSentinel()
    getOwner(1) != 0
    filtered { f -> noHavoc(f) && reachableOnly(f) }
    {
        preserved removeOwner(address prevOwner, address owner, uint256 _threshold) with (env e) {
            require isOwner(owner);
        }
    }


/// Two different owners must not point to the same owner
invariant uniqueOwnerPrevs(address prev1, address prev2)
    prev1 != prev2 && getOwner(prev1) != 0 => getOwner(prev1) != getOwner(prev2)
    filtered { f -> noHavoc(f) && reachableOnly(f) }
    {
        preserved removeOwner(address prevOwner, address owner, uint256 _threshold) with (env e) {
            require assert_uint256(getOwnerCount() - 1) >= _threshold;
            require isOwner(owner);
            require getOwner(prevOwner) == owner;
        }
    }

