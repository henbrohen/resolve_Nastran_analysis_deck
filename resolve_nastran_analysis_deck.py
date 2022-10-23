import pathlib

a_path = '/Users/henrikbrohenriksen/coding/python/projects/resolve_nastran_analysis_deck/a_deck.txt'


def write_to_file(file: pathlib.Path, data: str):
    with open(file, mode='at') as f:
        f.write(data)


def check_end_of_path(path: str, end_of_path: bool):

    path = path.strip()

    if path[-1] == "'" or path[-1] == '"':  # I.e. full path found.
        end_of_path = True
        path = path[:-1]
    else:
        end_of_path = False

    return path, end_of_path


def end_of_path_found(text: str, file: pathlib.Path, path: pathlib.Path):

    text = text + '$' + '-'*125 + '$\n'
    text = text + '$ Begin of file: ' + str(path) + '\n'
    text = text + '$' + '-'*125 + '$\n\n'
    write_to_file(file, text)
    text = ''

    return text


def read_text_file(text_file: pathlib.Path, output_file: pathlib.Path):
    
    # Verify that a file has been passed to the function and retrieve file path:
    if text_file.is_file():
        current_path = text_file.parent
        # path = text_file
    else:
        raise FileNotFoundError(print('File not found. Path given is not a file!'))

    end_of_path = True
    output_text = ''
    
    for line in text_file.open(mode='r'):
        
        if line.startswith("INCLUDE '") or line.startswith('INCLUDE "'):  # Read first part (or full part) of "INCLUDE" path.
            temp_path = line.strip()[9:]

            temp_path, end_of_path = check_end_of_path(temp_path, end_of_path)

            include_path = pathlib.Path(temp_path)

            if not include_path.is_absolute():
                include_path = current_path.joinpath(include_path).resolve()
            
            if end_of_path:
                output_text = end_of_path_found(output_text, output_file, include_path)
                read_text_file(include_path, output_file)  # Recursive function call to read new "INCLUDE" path.

        elif not end_of_path:  # I.e. the end of the include file path is not found yet.
            temp_path = line.strip()

            temp_path, end_of_path = check_end_of_path(temp_path, end_of_path)

            if temp_path.startswith('/'):  # Remove leading '/', to avoid pathlib treating it as an absolut path.
                temp_path = temp_path[1:]

            include_path = include_path.joinpath(temp_path)

            if end_of_path:
                output_text = end_of_path_found(output_text, output_file, include_path)
                read_text_file(include_path, output_file)  # Recursive function call to read new "INCLUDE" path.
        
        else:
            output_text = output_text + line.strip() + '\n'

    output_text = output_text + '$' + '-'*125 + '$\n'
    output_text = output_text + '$ End of file: ' + str(text_file) + '\n'
    output_text = output_text + '$' + '-'*125 + '$\n\n'
    
    write_to_file(output_file, output_text)


def resolve_analysis_deck(a_path: str):
    
    a_deck = pathlib.Path(a_path)
    resolved_a_deck = a_deck.parent.joinpath(a_deck.stem + '_resolved' + a_deck.suffix) 
    
    if resolved_a_deck.exists():
        resolved_a_deck.unlink()
    
    read_text_file(a_deck, resolved_a_deck)


if __name__ == '__main__':
    resolve_analysis_deck(a_path)
