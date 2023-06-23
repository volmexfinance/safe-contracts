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

/// Two different modules must not point to the same module
invariant uniqueOwnerPrevs(address prev1, address prev2)
    prev1 != prev2 && getOwner(prev1) != 0 => getOwner(prev1) != getOwner(prev2)
    filtered { f -> noHavoc(f) && reachableOnly(f) }
    { 
        preserved {
            requireInvariant noOwnerDeadEnds(getOwner(prev1), prev1);
            requireInvariant noOwnerDeadEnds(getOwner(prev2), prev2);
            requireInvariant uniqueOwnerPrevs(prev1, 1);
            requireInvariant uniqueOwnerPrevs(prev2, 1);
            requireInvariant uniqueOwnerPrevs(prev1, getOwner(prev2));
            requireInvariant uniqueOwnerPrevs(prev2, getOwner(prev1));
        }
        preserved swapOwner(address prevOwner, address oldOwner, address newOwner) with (env e) {
            requireInvariant uniqueOwnerPrevs(oldOwner, prev1);
            requireInvariant uniqueOwnerPrevs(oldOwner, prev2);
            requireInvariant noOwnerDeadEnds(newOwner, oldOwner);
            requireInvariant noOwnerDeadEnds(newOwner, prev1);
            requireInvariant noOwnerDeadEnds(newOwner, prev2);
        }
    }

/// An owner that points to the zero address must not have another owner pointing to it.
invariant noOwnerDeadEnds(address dead, address lost)
    dead != 0 && getOwner(dead) == 0 => getOwner(lost) != dead
    filtered { f -> noHavoc(f) && reachableOnly(f) }
    {
        preserved {
            requireInvariant liveOwnerSentinel();
            requireInvariant noOwnerDeadEnds(getOwner(1), 1);
        }
        preserved removeOwner(address prevOwner, address owner, uint256 threshold) with (env e) {
            requireInvariant uniqueOwnerPrevs(prevOwner, lost);
            requireInvariant uniqueOwnerPrevs(prevOwner, dead);
            requireInvariant noOwnerDeadEnds(dead, owner);
            requireInvariant noOwnerDeadEnds(owner, dead);
        }
        preserved swapOwner(address prevOwner, address oldOwner, address newOwner) with (env e) {
            requireInvariant noSelfPoint(oldOwner);
            requireInvariant noOwnerDeadEnds(oldOwner, prevOwner);
            requireInvariant noOwnerDeadEnds(dead, oldOwner);
            requireInvariant uniqueOwnerPrevs(prevOwner, lost);
        }
    }

invariant noSelfPoint(address self)
    self != 1 && self != 0 => getOwner(self) != self
    filtered { f -> noHavoc(f) && reachableOnly(f) }
    {
        preserved {
            requireInvariant noOwnerDeadEnds(getOwner(1), 1);
        }
        preserved removeOwner(address prevOwner, address owner, uint256 threshold) with (env e) {
            require getOwner(prevOwner) == owner && getOwner(owner) == prevOwner => owner == 1 || prevOwner == 1; // TODO: this needs to be proven as an invariant (sentinel always in the loop/ never more than 1 loop)
        }
        preserved swapOwner(address prevOwner, address oldOwner, address newOwner) with (env e) {
            requireInvariant noOwnerDeadEnds(self, oldOwner);
        }
    }

//invariant sentinelIncluded(address )