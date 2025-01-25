import os
from typing import List, Optional, Tuple
from rapidfuzz import process, distance
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from API_Database import retrieve_indivijual

load_dotenv()

class NameMatcher:
    """A class to match business names using fuzzy matching and LLM verification."""
    
    def __init__(self):
        """Initialize the NameMatcher with LLM and load environment variables."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Using 3.5 for cost efficiency
            api_key=api_key,
            temperature=0
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert in Indian business names and common variations."),
            ("user", """Query name: '{query}'
            Potential matches: {candidates}
            
            If one of the potential matches is clearly the same business (considering common variations, typos, or abbreviations), return that name.
            If none of the matches seem to be the same business, return 'None'.
            Response format: single line with match or 'None'""")
        ])

    def get_fuzzy_matches(self, query: str, database_names: List[str], limit: int = 10) -> List[Tuple[str, float]]:
        """Get initial matches using fuzzy matching.
        
        Args:
            query: The name to match against the database
            database_names: List of names from the database
            limit: Maximum number of matches to return
            
        Returns:
            List of tuples containing (name, score)
        """
        # Convert query to lowercase
        query = query.lower()
        
        # Convert all database names to lowercase for comparison
        lowercase_names = [name.lower() for name in database_names]
        
        # Get matches using lowercase versions
        matches = process.extract(
            query, 
            lowercase_names, 
            scorer=distance.JaroWinkler.distance, 
            limit=limit
        )
        
        # Map back to original case names
        original_case_matches = [
            (database_names[lowercase_names.index(match[0])], match[1]) 
            for match in matches
        ]
        
        return original_case_matches

    def verify_match(self, query: str, candidates: List[str]) -> Optional[str]:
        """Verify the best match using LLM.
        
        Args:
            query: The original query name
            candidates: List of potential matches
            
        Returns:
            The verified match or None if no confident match found
        """
        try:
            messages = self.prompt.format_messages(
                query=query,
                candidates=", ".join(candidates)
            )
            
            response = self.llm.invoke(messages)
            result = response.content.strip()
            
            # If the result is 'None' or not in candidates, return None
            return result if result in candidates else None
            
        except Exception as e:
            print(f"Error in LLM verification: {str(e)}")
            return None

    def find_match(self, query: str, entity_type: str = 'supplier') -> Optional[str]:
        """Find the best match for a query name in the database.
        
        Args:
            query: The name to match
            entity_type: Type of entity to match against ('supplier' or 'party')
            
        Returns:
            The best matching name or None if no confident match found
        """
        try:
            # Get all names from database
            data = retrieve_indivijual.get_all_names_ids(entity_type, dict_cursor=False)
            database_names = [y[1] for y in data]
            
            # Get fuzzy matches
            matches = self.get_fuzzy_matches(query, database_names)
            if not matches:
                return None
                
            # Extract just the names from matches
            candidate_names = [match[0] for match in matches]
            
            # Verify using LLM
            return self.verify_match(query, candidate_names)
            
        except Exception as e:
            print(f"Error in name matching: {str(e)}")
            return None

# Example usage:
# matcher = NameMatcher()
# result = matcher.find_match("rachit fashion", "supplier")
# print(f"Match found: {result}")
