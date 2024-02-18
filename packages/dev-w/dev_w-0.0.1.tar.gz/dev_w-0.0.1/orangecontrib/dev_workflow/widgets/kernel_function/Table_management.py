import Orange

def remove_meta(data_table_in):
    """
    This function removes metadata columns from the given Orange data table.

    :param data_table_in: Orange data table with both attributes and metadata columns.
    :return: New Orange data table containing only attribute columns (metadata removed).
    """
    # Call the function to filter and permute columns, selecting no metadata columns (empty list).
    return filter_and_permutate_column_meta(data_table_in, [])


# Function to create an Orange data table from a 2D array
def CreateOrangeDataTableFrom2dArray(vect_name_continuous_variable,
                                     vect_number_of_decimal_continuous_variable,
                                     vect_name_discrete_variable,
                                     vect_value_of_discrete_variable,
                                     meta_vect_name_string_variable,
                                     meta_vect_name_continous_variable,
                                     meta_vect_number_of_decimal_continuous_variable,
                                     meta_vect_name_discrete_variable,
                                     meta_vect_value_of_discrete_variable,
                                     array_2D_no_header):
    """
    This function takes several vectors and a 2D matrix as input to create an Orange data table.
    It constructs an Orange domain based on vectors of continuous variable names, decimal numbers, discrete variable names, discrete variable values, string variable names, continuous variable names, decimal numbers for continuous variables, discrete variable names for continuous variables, and discrete variable values for continuous variables.
    It returns an Orange data table based on the provided data.
    """
    # Checking vector sizes
    if len(vect_name_continuous_variable) != len(vect_number_of_decimal_continuous_variable):
        print("Error: Size mismatch in Domain Continuous Data")
        return None
    if len(vect_name_discrete_variable) != len(vect_value_of_discrete_variable):
        print("Error: Size mismatch in Domain Discrete Data")
        return None
    if len(meta_vect_name_continous_variable) != len(meta_vect_number_of_decimal_continuous_variable):
        print("Error: Size mismatch in Domain Continuous Data")
        return None
    if len(meta_vect_name_discrete_variable) != len(meta_vect_value_of_discrete_variable):
        print("Error: Size mismatch in Domain Discrete Data")
        return None

    # Checking column numbers in the 2D array
    nb_colonne = len(vect_name_continuous_variable) + len(vect_name_discrete_variable) + len(meta_vect_name_string_variable) + len(meta_vect_name_continous_variable) + len(meta_vect_name_discrete_variable)
    for i in range(len(array_2D_no_header)):
        if len(array_2D_no_header[i]) != nb_colonne:
            print("Error: Number of columns in header does not match number of columns at line ", i)
            return None

    # Creating attributes for continuous variables
    attributes = []
    for i in range(len(vect_name_continuous_variable)):
        attributes.append(Orange.data.ContinuousVariable(vect_name_continuous_variable[i], number_of_decimals=vect_number_of_decimal_continuous_variable[i]))

    # Creating attributes for discrete variables
    for i in range(len(vect_name_discrete_variable)):
        attributes.append(Orange.data.DiscreteVariable(vect_name_discrete_variable[i], values=vect_value_of_discrete_variable[i]))

    # Creating metas for string variables
    tab_meta = []
    for i in range(len(meta_vect_name_string_variable)):
        tab_meta.append(Orange.data.StringVariable(meta_vect_name_string_variable[i]))

    # Creating metas for continuous variables
    for i in range(len(meta_vect_name_continous_variable)):
        tab_meta.append(Orange.data.ContinuousVariable(meta_vect_name_continous_variable[i],
                                                       number_of_decimals=meta_vect_number_of_decimal_continuous_variable[i]))

    # Creating metas for discrete variables
    for i in range(len(meta_vect_name_discrete_variable)):
        tab_meta.append(Orange.data.DiscreteVariable(meta_vect_name_discrete_variable[i],
                                                    values=meta_vect_value_of_discrete_variable[i]))

    # Creating Orange domain
    domain = Orange.data.Domain(attributes, metas=tab_meta)

    # Example data
    array_2D_no_meta = [[1, 2, 3, 5, "apple", "cat", "cote de beaune", "blabla", "azert", 123.456, 987.123, "meta_apple", "meta_dog", "meta_beaugeolais"],
                        [4, 5, 6, 6, "orange", "cat", "champagne", "bliblbi", "yui", 1123.456, 1987.123, "meta_apple", "meta_dog", "meta_beaugeolais"],
                        [7, 8, 9, 9, "banana", "fish", "chardonnais", "tititoto", "azerar", 2123.456, 2987.123, "meta_banana", "meta_dog", "meta_champagne"],
                        [10, 11, 12, 12, "apple", "dog", "rully", "hehehe", "dfdf", 3123.456, 3987.123, "meta_cheery", "meta_fish", "meta_champagne"]]

    # Creating Orange data table
    return Orange.data.Table.from_list(domain, array_2D_no_header)


# ... (other functions)


# permutation
def filter_and_permutate_column_variable(Orange_data_table_in, vect_index_to_set_variable):
    """
    This function takes an Orange data table as input and a list of column indices to select, then returns a new Orange data table with only the selected columns, in the specified order.

    Parameters:
    - Orange_data_table_in (Orange.data.Table): Input Orange data table.
    - vect_index_to_set_variable (list of int): List of indices of columns to be selected.

    Returns:
    - Orange.data.Table: New Orange data table with selected columns.
    """
    # Selecting variables based on indices
    selected_vars = [Orange_data_table_in.domain[i] for i in vect_index_to_set_variable]

    # Creating a new domain with selected variables
    new_domain = Orange.data.Domain(selected_vars, Orange_data_table_in.domain.class_vars,
                                    Orange_data_table_in.domain.metas)

    # Creating a new data table with the selected domain
    new_data = Orange.data.Table.from_table(new_domain, Orange_data_table_in)

    # Returning the new data table
    return new_data


def filter_and_permutate_column_meta(Orange_data_table_in, vect_meta_index):
    """
    This function is similar to the previous one, but it selects metadata columns instead of attributes.

    Parameters:
    - Orange_data_table_in (Orange.data.Table): Input Orange data table.
    - vect_meta_index (list of int): List of indices of metadata columns to be selected.

    Returns:
    - Orange.data.Table: New Orange data table with selected metadata columns.
    """
    # Selecting metadata based on indices
    selected_metas = [Orange_data_table_in.domain.metas[i] for i in vect_meta_index]

    # Creating a new domain with selected metadata
    new_domain_metas = Orange.data.Domain(Orange_data_table_in.domain.attributes,
                                          Orange_data_table_in.domain.class_vars, selected_metas)

    # Creating a new data table with the selected metadata domain
    new_data_metas = Orange.data.Table.from_table(new_domain_metas, Orange_data_table_in)

    # Returning the new data table with selected metadata columns
    return new_data_metas


def GetListDiscreteFromListWithDoublon(input_list):
    """
    This function takes a list as input and returns a new list without duplicates. It is primarily used to obtain a list of unique discrete values.

    Parameters:
    - input_list (list): Input list containing potentially duplicate values.

    Returns:
    - list: New list containing unique values from the input list.
    """
    # Using the set data structure to remove duplicates and then converting it back to a list
    return list(set(input_list))


def saveTabWithSpecificExtension(orange_tab, filename):
    """
    This function takes an Orange data table and a file name as input, then saves the data table to a file with the ".tab" extension.

    Parameters:
    - orange_tab (Orange.data.Table): Orange data table to be saved.
    - filename (str): Name of the file to which the data table will be saved.

    Returns:
    - int: The function returns 0 upon successful completion.
    """
    # Get the writer for the ".tab" format
    writer = Orange.data.io.FileFormat.writers.get(".tab")

    # Write the data table to the specified file
    writer.write_file(filename, orange_tab)

    # Return 0 to indicate successful completion
    return 0


def loadTabWithSpecificExtension(filename):
    """
    This function takes a file name as input and loads an Orange data table from the file if it exists.

    Parameters:
    - filename (str): The name of the file from which to load the Orange data table.

    Returns:
    - Orange.data.Table: The loaded Orange data table if the file exists; otherwise, returns None.
    """
    # Create a TabReader object for reading Orange data tables
    tab_reader = Orange.data.io.TabReader(filename)

    # Read the data table from the specified file
    table_to_return = tab_reader.read()

    # Return the loaded Orange data table (or None if the file does not exist)
    return table_to_return


def GetLastLineOfOrangeDataTable(tab_in):
    """
    This function takes an Orange data table as input and returns the last line of data as lists, separating attributes from metadata.

    Parameters:
    - tab_in (Orange.data.Table): The input Orange data table.

    Returns:
    - tuple: A tuple containing two lists - the last line of attribute values and the last line of metadata values.
    """
    # Creating lists for attribute names and metadata names
    attribute_names = [element.name for element in tab_in.domain.attributes]
    print("attributes:", attribute_names)

    metadata_names = [element.name for element in tab_in.domain.metas]
    print("metadata:", metadata_names)

    # Getting the number of rows in the table
    nb_rows = len(tab_in)
    if nb_rows == 0:
        print("error: nb_rows == 0")
        return [], []

    # Getting the number of attribute columns
    nb_attribute_columns = len(attribute_names)

    # Extracting attribute values from the last line
    last_line_no_meta = [tab_in[nb_rows - 1, j].value for j in range(nb_attribute_columns)]

    # Extracting metadata values from the last line
    last_line_meta = [tab_in[nb_rows - 1, tab_in.domain.index(element)].value for element in metadata_names]

    # Returning a tuple containing the last line of attribute values and metadata values
    return last_line_no_meta, last_line_meta


def addlinetoOrangeTab(tab_in, array_data_in, array_meta_in):
    """
    This function takes an Orange data table, a list of data, and a list of metadata as input, then adds a new row to the existing data in the table.

    Parameters:
    - tab_in (Orange.data.Table): The input Orange data table.
    - array_data_in (list): The list of data to be added to the table.
    - array_meta_in (list): The list of metadata to be added to the table.

    Returns:
    - Orange.data.Table: A new Orange data table with the added row.
    """
    # Creating lists for attribute names and metadata names
    attribute_names = [element.name for element in tab_in.domain.attributes]
    metadata_names = [element.name for element in tab_in.domain.metas]

    # Getting the number of rows in the table
    nb_rows = len(tab_in)
    if nb_rows == 0:
        print("error: nb_rows == 0")
        return None

    # Getting the number of attribute columns
    nb_attribute_columns = len(attribute_names)

    # Extracting existing data from the table
    tab_of_data = [[tab_in[i, j].value for j in range(nb_attribute_columns)] +
                   [tab_in[i, tab_in.domain.index(element)].value for element in metadata_names] for i in range(nb_rows)]

    # Creating a new line with the given data and metadata
    new_line = array_data_in + array_meta_in
    tab_of_data.append(new_line)

    # Warning: not tested with discrete data
    print("warning: not tested with discrete data")

    # Returning a new Orange data table with the added row
    return Orange.data.Table.from_list(tab_in.domain, tab_of_data)


# Returns a dictionary with equivalences
def getIndexOfCategorical(table_with_cat):
    """
    This function returns a dictionary with equivalences for categorical variables.

    Parameters:
    - table_with_cat (Orange.data.Table): The input Orange data table with categorical variables.

    Returns:
    - dict: A dictionary containing equivalences for categorical variables where keys are variable names and values are dictionaries representing the mapping of values to indices.
    """
    out_index = {}
    for element in table_with_cat.domain:
        if hasattr(element, '_value_index'):
            out_index[element.name] = element._value_index
    return out_index


def substitutionCategoryToIndex(liste_domain_str, data_in, dict_index_to_categorical):
    """
    This function substitutes categorical values with their corresponding indices in the input data.

    Parameters:
    - liste_domain_str (list): List of variable names.
    - data_in (list of lists): Input data containing potentially categorical values.
    - dict_index_to_categorical (dict): Dictionary with equivalences for categorical variables where keys are variable names, and values are dictionaries representing the mapping of values to indices.

    Returns:
    - list of lists: Transformed data where categorical values are substituted with indices.
    """
    data_out = data_in.copy()
    for i, element in enumerate(liste_domain_str):
        print(i, element)
        if element in dict_index_to_categorical:
            for j in range(len(data_out)):
                data_out[j][i] = dict_index_to_categorical[element][data_out[j][i]]
    return data_out

def substitutionIndexToCategory(list_domain_str, data_in, dict_index_to_categorical):
    """
    This function substitutes indices with their corresponding categorical values in the input data.

    Parameters:
    - list_domain_str (list): List of variable names.
    - data_in (list of lists): Input data containing indices for categorical values.
    - dict_index_to_categorical (dict): Dictionary with equivalences for categorical variables where keys are variable names, and values are dictionaries representing the mapping of indices to values.

    Returns:
    - list of lists: Transformed data where indices are substituted with categorical values.
    """
    data_out = data_in.copy()
    for i, element in enumerate(list_domain_str):
        if element in dict_index_to_categorical:
            dico_toto = dict_index_to_categorical[element]
            dico_inverse = {v: k for k, v in dico_toto.items()}
            for j in range(len(data_out)):
                clef = int(round(data_out[j][i]))  # int not necessary, I think
                data_out[j][i] = dico_inverse[clef]
    return data_out



# Main block
if __name__ == "__main__":
    # Example data
    array_2D_no_header = [[1, 2, 3, 5, "apple", "cat", "cote de beaune", "blabla", "azert", 123.456, 987.123, "meta_apple", "meta_dog", "meta_beaugeolais"],
                          [4, 5, 6, 6, "orange", "cat", "champagne", "bliblbi", "yui", 1123.456, 1987.123, "meta_apple", "meta_dog", "meta_beaugeolais"],
                          [7, 8, 9, 9, "banana", "fish", "chardonnais", "tititoto", "azerar", 2123.456, 2987.123, "meta_banana", "meta_dog", "meta_champagne"],
                          [10, 11, 12, 12, "apple", "dog", "rully", "hehehe", "dfdf", 3123.456, 3987.123, "meta_cheery", "meta_fish", "meta_champagne"]]

    vect_name_continuous_variable = ["a", "b", "c", "d"]
    vect_number_of_decimal_continuous_variable = [6, 6, 6, 6]
    vect_name_discrete_variable = ["fruits", "animals", "wine"]
    vect_value_of_discrete_variable = [["apple", "orange", "banana", "peach", "cheery"],
                                       ["dog", "cat", "fish"],
                                       ["champagne", "beaugeolais", "chardonnais", "cote de beaune", "rully", "savigny les beaunes"]]

    meta_vect_name_string_variable = ["meta1", "meta2"]
    meta_vect_name_continous_variable = ["meta_continuous1", "meta_continuous2"]
    meta_vect_number_of_decimal_continuous_variable = [6, 6]
    meta_vect_name_discrete_variable = ["meta_fruits", "meta_animals", "meta_wine"]
    meta_vect_value_of_discrete_variable = [["meta_apple", "meta_orange", "meta_banana", "meta_peach", "meta_cheery"],
                                            ["meta_dog", "meta_cat", "meta_fish"],
                                            ["meta_champagne", "meta_beaugeolais", "meta_chardonnais", "meta_cote de beaune", "meta_rully",
                                             "meta_savigny les beaunes"]]

    # Creating Orange data table from the 2D array
    table_out = CreateOrangeDataTableFrom2dArray(vect_name_continuous_variable,
                                                 vect_number_of_decimal_continuous_variable,
                                                 vect_name_discrete_variable,
                                                 vect_value_of_discrete_variable,
                                                 meta_vect_name_string_variable,
                                                 meta_vect_name_continous_variable,
                                                 meta_vect_number_of_decimal_continuous_variable,
                                                 meta_vect_name_discrete_variable,
                                                 meta_vect_value_of_discrete_variable,
                                                 array_2D_no_header)

    # Saving the created table
    Orange.data.Table.save(table_out, "supp_moi_bis.tab")

    vect_index_to_set_variable=[0,2,5,3,4,1,6]#[0,2,1,6,5,4,3,7,8,9,10,11,12,13]
    table_deux=filter_and_permutate_column_variable(table_out, vect_index_to_set_variable)
    vect_index_to_set_meta = [6, 5, 4, 3, 2, 1, 0]
    table_trois = filter_and_permutate_column_meta(table_out, vect_index_to_set_meta)

    Orange.data.Table.save(table_trois, "supp_moi_bis_permutation_tototo.tab")
    saveTabWithSpecificExtension(table_trois,"zoubida.dada")
    loadTabWithSpecificExtension("zoubida.dada")
    print(GetLastLineOfOrangeDataTable(table_trois))
    Tab_4=addlinetoOrangeTab(table_trois,[14.0, 15.0, 16.0, 18.0, 'apple', 'dog', 'rully'],['meta_champagne', 'meta_fish', 'meta_cheery', 3.14, 987654, 'dfdf', 'hehehe'])
    saveTabWithSpecificExtension(Tab_4, "zoubida2.dada")
    exit()
    attributes = [Orange.data.ContinuousVariable("Min", number_of_decimals=6),
                  Orange.data.ContinuousVariable("Max", number_of_decimals=6),
                  Orange.data.ContinuousVariable("Step", number_of_decimals=6),
                  Orange.data.DiscreteVariable("fruit", values=["orange", "apple", "peach"])]
    domain = Orange.data.Domain(attributes, metas=[Orange.data.StringVariable("Name"),
                                                   Orange.data.ContinuousVariable("zoubida", number_of_decimals=6),
                                                   Orange.data.DiscreteVariable("sexe", values=["homme", "femme", "autre"])])
    table = Orange.data.Table.from_list(domain, [[1,2,3,"apple","alors",1.1,"homme"],[5,6,7,"peach","qu est ce",1.2,"femme"],[9,10,11,"orange","qu on attend",1.3,"autre"]])
