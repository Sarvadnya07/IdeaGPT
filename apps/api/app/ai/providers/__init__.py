"""
DEPRECATED legacy AI provider package.

The canonical provider implementation lives in ``app.ai.gateway.providers``
(``BaseProviderAdapter`` implementations registered with
``app.ai.gateway.registry.gateway_registry``).

Everything under this package exists only so the gateway transition could be
done without a flag day. New provider work must target the gateway adapters.
Import of this package outside ``app/ai/orchestrator/`` is rejected by
``tests/test_architecture_fitness.py``.
"""
