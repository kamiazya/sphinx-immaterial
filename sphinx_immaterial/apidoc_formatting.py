"""Modifies the formatting of API documentation."""

from typing import TYPE_CHECKING

import docutils.nodes
import sphinx.addnodes
import sphinx.application
import sphinx.locale
import sphinx.writers.html5

_ = sphinx.locale._

SIGNATURE_WRAP_LENGTH = 70

if TYPE_CHECKING:
    HTMLTranslatorMixinBase = sphinx.writers.html5.HTML5Translator
else:
    HTMLTranslatorMixinBase = object


class HTMLTranslatorMixin(HTMLTranslatorMixinBase):  # pylint: disable=abstract-method
    """Mixin for HTMLTranslator that adds additional CSS classes."""

    def visit_desc(self, node: sphinx.addnodes.desc) -> None:
        # Object description node

        # These are converted to `<dl>` elements with the domain and objtype
        # as classes.

        # Augment the list of classes with `objdesc` to make it easier to
        # style these without resorting to hacks.
        node["classes"].append("objdesc")
        super().visit_desc(node)

    def visit_desc_type(self, node: sphinx.addnodes.desc_type) -> None:
        self.body.append(
            self.starttag(node, tagname="span", suffix="", CLASS="desctype")
        )

    def depart_desc_type(self, node: sphinx.addnodes.desc_type) -> None:
        self.body.append("</span>")

    def visit_desc_signature(self, node: sphinx.addnodes.desc_signature) -> None:
        node_text = node.astext()
        # add highlight to invoke syntax highlighting in CSS
        node["classes"].append("highlight")
        if len(node_text) > SIGNATURE_WRAP_LENGTH:
            node["classes"].append("sig-wrap")
        super().visit_desc_signature(node)

    def visit_desc_parameterlist(
        self, node: sphinx.addnodes.desc_parameterlist
    ) -> None:
        super().visit_desc_parameterlist(node)
        open_paren, _ = node.get("parens", ("(", ")"))
        self.body[-1] = self.body[-1].replace("(", open_paren)

    def depart_desc_parameterlist(
        self, node: sphinx.addnodes.desc_parameterlist
    ) -> None:
        super().depart_desc_parameterlist(node)
        _, close_paren = node.get("parens", ("(", ")"))
        self.body[-1] = self.body[-1].replace(")", close_paren)

    def visit_desc_parameter(self, node: sphinx.addnodes.desc_parameter) -> None:
        self.body.append('<span class="sig-param-decl">')
        super().visit_desc_parameter(node)

    def depart_desc_parameter(self, node: sphinx.addnodes.desc_parameter) -> None:
        super().depart_desc_parameter(node)
        self.body.append("</span>")

    def depart_field_name(self, node: docutils.nodes.Element) -> None:
        self.add_permalink_ref(node, _("Permalink to this headline"))
        super().depart_field_name(node)

    def depart_term(self, node: docutils.nodes.Element) -> None:
        if "ids" in node:
            self.add_permalink_ref(node, _("Permalink to this definition"))
        super().depart_term(node)

    def visit_caption(self, node: docutils.nodes.Element) -> None:
        attributes = {"class": "caption-text"}
        if isinstance(node.parent, docutils.nodes.container) and node.parent.get(
            "literal_block"
        ):
            # add highlight class to caption's div container.
            # This is needed to trigger mkdocs-material CSS rule `.highlight .filename`
            self.body.append('<div class="code-block-caption highlight">')
            # append a CSS class to trigger mkdocs-material theme's caption CSS style
            attributes["class"] += " filename"
        else:
            super().visit_caption(node)
        self.add_fignumber(node.parent)
        self.body.append(self.starttag(node, "span", **attributes))

    def depart_caption(self, node: docutils.nodes.Element) -> None:
        if not isinstance(
            node.parent, docutils.nodes.container
        ) and not node.parent.get("literal_block"):
            # only append ending tag if parent is not a literal-block.
            # Because all elements in the caption should be within a span element
            self.body.append("</span>")

        # append permalink if available
        if isinstance(node.parent, docutils.nodes.container) and node.parent.get(
            "literal_block"
        ):
            self.add_permalink_ref(node.parent, _("Permalink to this code"))
            self.body.append("</span>")  # done; add closing tag
        elif isinstance(node.parent, docutils.nodes.figure):
            self.add_permalink_ref(node.parent, _("Permalink to this image"))
        elif node.parent.get("toctree"):
            self.add_permalink_ref(node.parent.parent, _("Permalink to this toctree"))

        if isinstance(node.parent, docutils.nodes.container) and node.parent.get(
            "literal_block"
        ):
            self.body.append("</div>\n")
        else:
            super().depart_caption(node)




def setup(app: sphinx.application.Sphinx):
    """Registers the monkey patches.

    Does not register HTMLTranslatorMixin, the caller must do that.
    """
    # Add "highlight" class in order for pygments syntax highlighting CSS rules
    # to apply.
    sphinx.addnodes.desc_signature.classes.append("highlight")

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
