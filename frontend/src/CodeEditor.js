import React from 'react';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs/components/prism-core';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism.css'; //Example style, you can use another

const CodeEditor = ({ code, setCode }) => {
    return (
        <Editor
            value={code}
            onValueChange={code => setCode(code)}
            highlight={code => highlight(code, languages.python)}
            padding={10}
            style={{
                fontFamily: '"Fira code", "Fira Mono", monospace',
                fontSize: 12,
                border: '1px solid #ddd',
                borderRadius: '5px',
                minHeight: '200px',
                backgroundColor: '#f5f5f5'
            }}
        />
    );
};

export default CodeEditor;
