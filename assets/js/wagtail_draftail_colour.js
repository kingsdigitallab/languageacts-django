
/**
 * A React component that renders nothing.
 * We actually create the entities directly in the componentDidMount lifecycle hook.
 */
// Warning: This code uses ES2015+ syntax, it will not work in IE11.



class ColourSource extends React.Component {
    componentDidMount() {
        const { editorState, entityType, onComplete } = this.props;

        const content = editorState.getCurrentContent();

        var body = document.getElementById('wagtail');
        var picker = document.createElement('div');
        picker.setAttribute('id', 'picker');

        picker.innerHTML = '<div class="wrap"><h2>Choose Colour</h2><ul><li class="colour-selection black-bg" style="background-color: #0a0a0a" data-color="#0a0a0a"></li><li class="colour-selection green-bg" style="background-color: #4caf50" data-color="#4caf50"></li><li class="colour-selection lightgreen-bg" style="background-color: #8cc152" data-color="#8cc152"></li><li class="colour-selection yellow-bg" style="background-color: #f7de30" data-color="#f7de30"></li><li class="colour-selection orange-bg" style="background-color: #fd9727" data-color="#fd9727"></li><li class="colour-selection deeporange-bg" style="background-color: #fc5830"  data-color="#fc5830"></li><li class="colour-selection red-bg" style="background-color: #e53935"  data-color="#e53935"></li><li class="colour-selection deeppurple-bg" style="background-color: #673fb4"  data-color="#673fb4"></li><li class="colour-selection blue-bg" style="background-color: #1976d2" data-color="#1976d2"></li><li class="colour-selection lightblue-bg active" style="background-color: #039be5"  data-color="#039be5"></li></ul></div>';
        body.appendChild(picker);

        var lis = document.getElementsByClassName('colour-selection')
        for(var i = 0; i < lis.length; i++) {
            (function(index) {
              lis[index].addEventListener("click", function(){
                   cont(content, entityType, editorState, onComplete, this.getAttribute("data-color"));
                   picker.remove();
                });
            })(i);
        }
    }


    constructor(props) {
        super(props);
        this.state = {
          // modal should be closed on page load
          isModalOpen: false
        };
        
        // binding methods
        this.openModal = this.openModal.bind(this);
        this.closeModal = this.closeModal.bind(this);
      }
      
      openModal() {
        this.setState({ isModalOpen: true})
      }
      
      closeModal () {
        this.setState({ isModalOpen: false })
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


function cont(content, entityType, editorState, onComplete, fragment)
{
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