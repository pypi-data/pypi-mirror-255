from __future__ import annotations

from typing import Collection, List, Optional, cast
import logging

from sarus_data_spec.constants import NO_TOKEN, PEP_TOKEN
from sarus_data_spec.dataspec_rewriter.utils import graph_private_queries
from sarus_data_spec.dataspec_validator.base import BaseDataspecValidator
from sarus_data_spec.dataspec_validator.privacy_limit import DeltaEpsilonLimit
from sarus_data_spec.manager.ops.processor import routing
from sarus_data_spec.storage.typing import Storage
from sarus_data_spec.variant_constraint import pep_for_rewriting_constraint
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st

logger = logging.getLogger(__name__)


class RecursiveDataspecValidator(BaseDataspecValidator):
    def __init__(self, storage: Storage):
        self._storage = storage

    # Local property
    def is_dp_able(self, dataspec: st.DataSpec) -> bool:
        """Checks if the dataspec has a transform that either has a DP
        equivalent, allowing the rewritten dataspec to be considered DP
        if the input rewritten PEP token is not None."""
        if not dataspec.is_transformed():
            return False

        if dataspec.is_dp():
            return True

        _, StaticChecker = routing.get_op(dataspec)
        return StaticChecker(dataspec).is_dp_able()

    def is_pep_able(self, dataspec: st.DataSpec) -> bool:
        """Checks if the dataspec has a transform that either has a PEP
        equivalent or does not require one, allowing the rewritten dataspec to
        be considered 'PEP' if the input rewritten PEP token is not None."""
        if dataspec.is_pep():
            return True

        _, StaticChecker = routing.get_op(dataspec)
        return StaticChecker(dataspec).is_pep_able()

    def is_dp_writable(self, dataspec: st.DataSpec) -> bool:
        if not self.is_dp_able(dataspec):
            return False

        if dataspec.is_dp():
            return True

        _, StaticChecker = routing.get_op(dataspec)
        return StaticChecker(dataspec).is_dp_writable([])

    def is_pep_writable(self, dataspec: st.DataSpec) -> bool:
        if not self.is_pep_able(dataspec):
            return False

        return self.rewritten_pep_token(dataspec) is not None

    def is_publishable(self, dataspec: st.DataSpec) -> bool:
        if not dataspec.is_transformed():
            return False

        if self.is_dp_writable(dataspec):
            return True

        parents = dataspec.parents_list()
        return all(
            [
                self.is_publishable(dataspec_parent)
                for dataspec_parent in parents
            ]
        )

    def is_published(self, dataspec: st.DataSpec) -> bool:
        """Check if the dataspec is the result of a DP transform or another
        published dataspec.
        There is at least one parent that is DP.
        Such a dataspec has at least one private query in its computation
        graph."""
        if not dataspec.is_transformed():
            return False

        if dataspec.is_dp():
            return True

        parents = dataspec.parents_list()
        return all(
            [self.is_published(dataspec_parent) for dataspec_parent in parents]
        )

    def rewritten_pep_token(self, dataspec: st.DataSpec) -> Optional[str]:
        """Returns the PEP token for the DP variant of this dataspec
        during DP rewriting.

        Currently, the implementation assumes a single DP/PEP variant per
        dataspec, resulting in one possible value for
        "rewritten_pep_token."
        Future changes could introduce multiple variants, necessitating
        the implementation of priority rules.
        """
        if dataspec.prototype() == sp.Scalar:
            return None

        dataset = cast(st.Dataset, dataspec)

        # TODO fetch real context and budget
        public_context: Collection[str] = []
        privacy_limit = DeltaEpsilonLimit({0.0: 0.0})
        kind = st.ConstraintKind.PEP_FOR_REWRITING

        for constraint in self.verified_constraints(dataspec):
            check_constraint = self.verifies(
                constraint, kind, public_context, privacy_limit
            )
            if check_constraint is not None:
                if check_constraint:
                    return constraint.properties()[PEP_TOKEN]
                else:
                    return None

        # Compute the PEP token
        if not dataset.is_transformed():
            return None

        transform = dataset.transform()
        _, StaticChecker = routing.get_dataset_op(transform)
        pep_token = StaticChecker(dataset).rewritten_pep_token(public_context)
        if pep_token is None:
            pep_token = NO_TOKEN

        pep_for_rewriting_constraint(
            dataspec=dataset,
            token=pep_token,
            required_context=[],
            privacy_limit=privacy_limit,
        )

        return None if pep_token == NO_TOKEN else pep_token

    def graph_private_queries(
        self, dataspec: st.DataSpec
    ) -> List[st.PrivateQuery]:
        """Return the list of PrivateQueries used in a Dataspec's transform.

        This method collect all the private queries of the  computation graph.

        It represents the privacy loss associated with the current computation.

        It can be used by Sarus when a user (Access object) reads a DP dataspec
        to update its accountant. Note that Private Query objects are generated
        with a random uuid so that even if they are submitted multiple times to
        an account, they are only accounted once (ask @cgastaud for more on
        accounting).
        """
        return graph_private_queries(dataspec)
