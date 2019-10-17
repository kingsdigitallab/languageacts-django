
/**
 * A React component that renders nothing.
 * We actually create the entities directly in the componentDidMount lifecycle hook.
 */
// Warning: This code uses ES2015+ syntax, it will not work in IE11.
class ColourSource extends React.Component {
    componentDidMount() {
        const { editorState, entityType, onComplete } = this.props;

        const content = editorState.getCurrentContent();

        const fragment = window.prompt('Fragment identifier:');

        // Uses the Draft.js API to create a new entity with the right data.
        const contentWithEntity = content.createEntity(
            entityType.type,
            'MUTABLE',
            {
                fragment: fragment,
            },
        );
        const entityKey = contentWithEntity.getLastCreatedEntityKey();
        const selection = editorState.getSelection();
        const nextState = RichUtils.toggleLink(
            editorState,
            selection,
            entityKey,
        );

        onComplete(nextState);
    }

    render() {
        return null;
    }
}

const Colour = props => {
    const { entityKey, contentState } = props;
    const data = contentState.getEntity(entityKey).getData();

    return React.createElement(
        'span',
        {
            class: 'hello',
            style: { color: data.fragment},
            'data-colour': data.fragment,
        },
        props.children,
    );
};

window.draftail.registerPlugin({
    type: 'COLOUR',
    source: ColourSource,
    decorator: Colour,
});

