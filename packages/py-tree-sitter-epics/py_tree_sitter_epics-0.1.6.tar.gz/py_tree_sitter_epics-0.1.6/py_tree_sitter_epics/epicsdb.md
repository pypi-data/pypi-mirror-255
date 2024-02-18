## EPICS DB

Based on tree-sitter-epics structure, this python class has the following structure.

``` mermaid
classDiagram
    Record--o Link : 0..1
    DbParser --|> Record :  0..*
    
    class Link {
        set_record_name()
        set_type_link()
        create_link()
        string record_name
        string type_link
    }

    class Record {
        print_to_text()
        string record_type 
        string record_name 
        string description 
        tuple[string,string] fields 
        string unit
        string description
        string infos
        List<Link> links_in
        List<Link> links_out
    }
        
    class DbParser {
        parse()
        parserTree
    }

   
```
