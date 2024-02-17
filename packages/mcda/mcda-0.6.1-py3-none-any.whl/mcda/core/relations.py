from __future__ import annotations

import sys
from abc import ABC
from typing import Any, Dict, Iterator, List, Tuple, Union, cast

from graphviz import Digraph
from numpy import fill_diagonal
from pandas import DataFrame, Series

from .matrices import OutrankingMatrix, create_outranking_matrix
from .scales import PreferenceDirection, QuantitativeScale
from .values import Ranking

if sys.version_info >= (3, 11):  # pragma: nocover
    from typing import Self
else:
    from typing_extensions import Self


class Relation(ABC):
    """This class represents a pairwise relation between two elements.

    :param a: first element
    :param b: second element

    :attribute a:
    :attribute b:
    :attribute DRAW_STYLE: (class) key args for plotting all instances
    """

    _RELATION_TYPE = ""
    DRAW_STYLE: Dict[str, Any] = {"style": "invis"}

    def __init__(self, a: Any, b: Any):
        self.a = a
        self.b = b
        self.validate()

    def __str__(self) -> str:
        """Return string representation of object.

        :return:
        """
        return f"{self.a} {self._RELATION_TYPE} {self.b}"

    def __repr__(self) -> str:  # pragma: nocover
        """Return representation of object.

        :return:
        """
        return f"{self.__class__.__name__}({self.a}, {self.b})"

    @property
    def elements(self) -> Tuple[Any, Any]:
        """Return elements of the relation"""
        return self.a, self.b

    def validate(self):
        """Check whether a relation is valid or not."""
        pass

    def same_elements(self, relation: Relation) -> bool:
        """Check whether the relations are about the same pair of alternatives.

        :param relation: second relation
        :return:
            ``True`` if both relations share the same elements pair, ``False``
            otherwise

        .. warning:: Does not check for relations' validity!
        """
        return set(self.elements) == set(relation.elements)

    def __eq__(self, other: Any) -> bool:
        """Check whether relations are equal.

        :param other:
        :return: check result

        .. warning:: Does not check for relations' validity!
        """
        if type(other) == type(self):
            return self.elements == other.elements
        return False

    def __add__(self, other: Relation) -> PreferenceStructure:
        """Build new preference structure as addition of both relations.

        :return: relations added to new preference structure
        """
        if not isinstance(other, Relation):
            raise TypeError("can only add one other Relation object")
        return PreferenceStructure([self, other])

    def __hash__(self) -> int:
        """Hash object based on its unordered list of elements"""
        return hash(self.a) + hash(self.b)

    def compatible(self, other: Relation) -> bool:
        """Check whether both relations can coexist in the same preference
        structure.

        Relations are compatible if equal or having different elements pair.

        :param other:
        :return: check result

        .. warning:: Does not check for relations' validity!
        """
        return self == other or not self.same_elements(other)

    @classmethod
    def types(cls) -> List:
        """Return list of relation types.

        :return:
        """
        return cls.__subclasses__()

    def _draw(self, graph: Digraph):
        """Draw relation on provided graph"""
        graph.edge(str(self.a), str(self.b), **self.DRAW_STYLE)


class PreferenceRelation(Relation):
    """This class represents a preference relation between two elements.

    A relation is read `aPb`.

    :param a: first element
    :param b: second element

    :attribute a:
    :attribute b:
    :attribute DRAW_STYLE: (class) key args for plotting all instances

    .. note:: this relation is antisymmetric and irreflexive
    """

    _RELATION_TYPE = "P"
    DRAW_STYLE: Dict[str, Any] = {}

    def validate(self):
        """Check whether a relation is valid or not.

        :raise ValueError: if relation is reflexive
        """
        if self.a == self.b:
            raise ValueError(
                f"Preference relations are irreflexive: {self.a} == {self.b}"
            )


class IndifferenceRelation(Relation):
    """This class represents an indifference relation between two elements.

    A relation is read `aIb`.

    :param a: first element
    :param b: second element

    :attribute a:
    :attribute b:
    :attribute DRAW_STYLE: (class) key args for plotting all instances

    .. note:: this relation is symmetric and reflexive
    """

    _RELATION_TYPE = "I"
    DRAW_STYLE = {"arrowhead": "none"}

    __hash__ = Relation.__hash__

    def __eq__(self, other):
        """Check whether relations are equal.

        :param other:
        :return: check result

        .. warning:: Does not check for relations' validity!
        """
        if type(other) == type(self):
            return self.same_elements(other)
        return False


class IncomparableRelation(Relation):
    """This class represents an incomparable relation between two elements.

    A relation is read `aRb`.

    :param a: first element
    :param b: second element

    :attribute a:
    :attribute b:
    :attribute DRAW_STYLE: (class) key args for plotting all instances

    .. note:: this relation is symmetric and irreflexive
    """

    _RELATION_TYPE = "R"
    DRAW_STYLE = {"arrowhead": "none", "style": "dotted"}

    __hash__ = Relation.__hash__

    def __eq__(self, other):
        """Check whether relations are equal.

        :param other:
        :return: check result

        .. warning:: Does not check for relations' validity!
        """
        if type(other) == type(self):
            return self.same_elements(other)
        return False

    def validate(self):
        """Check whether a relation is valid or not.

        :raise ValueError: if relation is reflexive
        """
        if self.a == self.b:
            raise ValueError(
                f"Incomparable relations are irreflexive: {self.a} == {self.b}"
            )


P = PreferenceRelation
"""Type alias for user-friendly definition of :class:`PreferenceRelation`"""


I = IndifferenceRelation  # noqa: E741
"""Type alias for user-friendly definition of :class:`IndifferenceRelation`"""


R = IncomparableRelation
"""Type alias for user-friendly definition of :class:`IncomparableRelation`"""


class PreferenceStructure:
    """This class represents a list of relations.

    Any type of relations is accepted, so this represents the union of P, I and
    R.

    :param data:
    """

    def __init__(
        self,
        data: Union[
            List[Relation], Relation, PreferenceStructure, None
        ] = None,
    ):
        data = [] if data is None else data
        if isinstance(data, Relation):
            relations = [data]
        elif isinstance(data, PreferenceStructure):
            relations = data.relations
        else:
            relations = data
        self._relations = list(set(relations))
        self.validate()

    @property
    def elements(self) -> List:
        """Return elements present in relations list."""
        return sorted(set(e for r in self._relations for e in r.elements))

    @property
    def relations(self) -> List[Relation]:
        """Return copy of relations list."""
        return self._relations.copy()

    def validate(self):
        """Check whether the relations are all valid.

        :raise ValueError: if at least two relations are incompatible
        """
        for i, r1 in enumerate(self._relations):
            for r2 in self._relations[(i + 1) :]:
                if not r1.compatible(r2):
                    raise ValueError(f"incompatible relations: {r1}, {r2}")

    @property
    def is_total_preorder(self) -> bool:
        """Check whether relations list is a total preorder or not"""
        return (
            len(
                PreferenceStructure(
                    self.transitive_closure[IncomparableRelation]
                )
            )
            == 0
        )

    @property
    def is_total_order(self) -> bool:
        """Check whether relations list is a total order or not"""
        res = self.transitive_closure
        return (
            len(PreferenceStructure(res[IncomparableRelation]))
            + len(PreferenceStructure(res[IndifferenceRelation]))
            == 0
        )

    def __eq__(self, other: Any):
        """Check if preference structure is equal to another.

        Equality is defined as having the same set of relations.

        :return:

        .. note:: `other` type is not coerced
        """
        if isinstance(other, PreferenceStructure):
            return set(other.relations) == set(self._relations)
        return False

    def __len__(self) -> int:
        """Return number of relations in the preference structure.

        :return:
        """
        return len(self._relations)

    def __str__(self) -> str:
        """Return string representation of relations.

        :return:
        """
        return "[" + ", ".join([str(r) for r in self._relations]) + "]"

    def __repr__(self) -> str:  # pragma: nocover
        """Return representation of relations contained in structure

        :return:
        """
        return f"{self.__class__.__name__}({repr(self._relations)})"

    def _relation(
        self,
        *args: Any,
    ) -> Union[Relation, PreferenceStructure, None]:
        """Return all relations between given elements of given types.

        If no relation type is supplied, all are considered.
        If no element is supplied, all are considered.

        :param *args:
        :return:

        .. warning:: Does not check for a relation's validity or redundancy!
        """
        elements = []
        types = []
        for arg in args:
            if isinstance(arg, type) and issubclass(arg, Relation):
                types.append(arg)
            else:
                elements.append(arg)
        elements = self.elements if len(elements) == 0 else elements
        types = Relation.types() if len(types) == 0 else types
        res = None
        for r in self._relations:
            if r.a in elements and r.b in elements and r.__class__ in types:
                res = r if res is None else cast(Relation, res) + r
        return res

    def _element_relations(
        self, a: Any
    ) -> Union[Relation, PreferenceStructure, None]:
        """Return all relations involving given element.

        :param a: element
        :return:

        .. warning:: Does not check for a relation's validity or redundancy!
        """
        res = None
        for r in self._relations:
            if a in r.elements:
                res = r if res is None else cast(Relation, res) + r
        return res

    def __getitem__(
        self, item: Any
    ) -> Union[Relation, PreferenceStructure, None]:
        """Return all relations matching the request

        :param item:
        :return:
            Depending on `item` type:
                * pair of elements: search first relation with this elements
                pair
                * element: all relations involving element
                * relation class: all relations of this class
        """
        if isinstance(item, tuple):
            return self._relation(*item)
        if isinstance(item, type):
            return self._relation(item)
        return self._element_relations(item)

    def __delitem__(self, item: Any):
        """Remove all relations matching the request

        :param item:
        :return:
            Depending on `item` type:
                * pair of elements: search first relation with this elements
                pair
                * element: all relations involving element
                * relation class: all relations of this class
        """
        r = self[item]
        to_delete = PreferenceStructure(r)._relations
        self._relations = [rr for rr in self._relations if rr not in to_delete]

    def __contains__(self, item: Any) -> bool:
        """Check whether a relation is already in the preference structure.

        :param item: relation
        :return: check result

        .. warning:: Does not check for a relation's validity!
        """
        for r in self._relations:
            if r == item:
                return True
        return False

    def __add__(self, other: Any) -> PreferenceStructure:
        """Create new preference structure with appended relations.

        :param other:
            * :class:`Relation`: relation is appended into new object
            * :class:`PreferenceStructure`: all relations are appended into new
            object
        :return:
        """
        if hasattr(other, "__iter__"):
            return self.__class__(self._relations + [r for r in other])
        return self.__class__(self._relations + [other])

    def __iter__(self) -> Iterator[Relation]:
        """Return iterator over relations

        :return:
        """
        return iter(self._relations)

    @classmethod
    def from_ranking(cls, ranking: Ranking) -> Self:
        """Convert ranking into preference structure.

        :param ranking:
        :return:

        .. note::
            The minimum number of relations representing the scores is returned
            (w.r.t transitivity of preference and indifference relations)
        """
        res: List[Relation] = []
        for i, a in enumerate(ranking.labels):
            for b in ranking.labels[(i + 1) :]:
                if ranking[a] == ranking[b]:
                    res.append(IndifferenceRelation(a, b))
                elif ranking.scale.is_better(ranking[a], ranking[b]):
                    res.append(PreferenceRelation(a, b))
                else:
                    res.append(PreferenceRelation(b, a))
        return cls(res)

    @classmethod
    def from_outranking_matrix(
        cls, outranking_matrix: OutrankingMatrix
    ) -> Self:
        """Convert outranking matrix to preference structure.

        :param outranking_matrix:
        :return:
        """
        relations: List[Relation] = list()
        for ii, i in enumerate(outranking_matrix.vertices):
            for j in outranking_matrix.vertices[ii + 1 :]:
                if outranking_matrix.data.at[i, j]:
                    if outranking_matrix.data.at[j, i]:
                        relations.append(IndifferenceRelation(i, j))
                    else:
                        relations.append(PreferenceRelation(i, j))
                elif outranking_matrix.data.at[j, i]:
                    relations.append(PreferenceRelation(j, i))
                else:
                    relations.append(IncomparableRelation(i, j))
        return cls(relations)

    @property
    def ranking(self) -> Ranking:
        """Convert preference structure to ranking.

        :raises ValueError: if `preference_structure` is not a total pre-order
        :return:

        .. note:: returned ranking goes for 0 to n-1 (with 0 the best rank)
        """
        if not self.is_total_preorder:
            raise ValueError(
                "only total pre-order can be represented as Ranking"
            )
        s = Series(0, index=self.elements)
        pref_copy = self.transitive_closure
        while len(pref_copy.elements) > 0:
            bad_alternatives = set()
            for r in PreferenceStructure(pref_copy[PreferenceRelation]):
                bad_alternatives.add(r.b)
            s[[*bad_alternatives]] += 1
            for a in set(pref_copy.elements) - bad_alternatives:
                del pref_copy[a]
        return Ranking(
            s,
            QuantitativeScale(preference_direction=PreferenceDirection.MIN),
        )

    @property
    def outranking_matrix(self) -> OutrankingMatrix:
        """Transform a preference structure into an outranking matrix.

        :return: outranking matrix
        """
        elements = self.elements
        matrix = DataFrame(0, index=elements, columns=elements)
        fill_diagonal(matrix.values, 1)
        for r in self:
            a, b = r.elements
            if isinstance(r, PreferenceRelation):
                matrix.at[a, b] = 1
            if isinstance(r, IndifferenceRelation):
                matrix.at[a, b] = 1
                matrix.at[b, a] = 1
        return create_outranking_matrix(matrix)

    @property
    def transitive_closure(self) -> PreferenceStructure:
        """Apply transitive closure to preference structure and return result.

        .. warning:: Does not check for a valid preference structure!
        """
        return PreferenceStructure.from_outranking_matrix(
            self.outranking_matrix.transitive_closure
        )

    @property
    def transitive_reduction(self) -> PreferenceStructure:
        """Apply transitive reduction to preference structure and return result

        .. warning:: Does not check for a valid preference structure!

        .. warning:: This function may bundle together multiple elements
        """
        return PreferenceStructure.from_outranking_matrix(
            self.outranking_matrix.transitive_reduction
        )

    def plot(self) -> Digraph:
        """Create graph from preference structure and plot it.

        :return: graph

        .. note::
            You need an environment that will actually display the graph (such
            as a jupyter notebook), otherwise the function only returns the
            graph.
        """
        relation_graph = Digraph("relations", strict=True)
        relation_graph.attr("node", shape="box")
        for e in self.elements:
            relation_graph.node(str(e))
        for r in self._relations:
            r._draw(relation_graph)
        return relation_graph

    def save_plot(self) -> str:  # pragma: nocover
        """Plot preference structure as a graph and save it.

        :return: file name where plot is saved
        """
        return self.plot().render()

    def copy(self) -> PreferenceStructure:
        """Copy preference structure into new object.

        :return: copy
        """
        return PreferenceStructure(self)
