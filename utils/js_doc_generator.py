#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Générateur de documentation JavaScript pour le projet Madsea

Ce script analyse les fichiers JavaScript du projet et génère une documentation
structurée au format Markdown. Il est particulièrement utile pour documenter
les modules de style comme Déclic Ombre Chinoise.
"""

import os
import re
import json
import argparse
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class JSDocGenerator:
    """Générateur de documentation pour les fichiers JavaScript"""

    def __init__(self, js_dir, output_dir):
        """
        Initialise le générateur de documentation
        
        Args:
            js_dir (str): Répertoire contenant les fichiers JavaScript
            output_dir (str): Répertoire de sortie pour la documentation
        """
        self.js_dir = Path(js_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Modèles de regex pour l'analyse
        self.class_pattern = re.compile(r'class\s+([\w]+)\s*{')
        self.method_pattern = re.compile(r'\s+([\w]+)\s*\([^)]*\)\s*{')
        self.comment_pattern = re.compile(r'/\*\*([\s\S]*?)\*/')
        self.property_pattern = re.compile(r'this\.([\w]+)\s*=')
        
        # Structure pour stocker les informations extraites
        self.modules = {}

    def parse_js_files(self):
        """Analyse tous les fichiers JavaScript dans le répertoire spécifié"""
        js_files = list(self.js_dir.glob('**/*.js'))
        logger.info(f"Trouvé {len(js_files)} fichiers JavaScript à analyser")
        
        for js_file in js_files:
            try:
                self.parse_js_file(js_file)
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de {js_file}: {e}")
    
    def parse_js_file(self, file_path):
        """Analyse un fichier JavaScript spécifique"""
        logger.info(f"Analyse du fichier {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire les commentaires de module
        module_doc = ""
        module_comments = self.comment_pattern.findall(content)
        if module_comments and '* ' in module_comments[0]:
            module_doc = self._clean_comment(module_comments[0])
        
        # Extraire les classes
        classes = {}
        class_matches = self.class_pattern.findall(content)
        
        for class_name in class_matches:
            # Trouver la définition complète de la classe
            class_start = content.find(f"class {class_name}")
            
            # Chercher le commentaire de classe précédent
            class_doc = ""
            class_comment_match = re.search(r'/\*\*([\s\S]*?)\*/\s*class\s+' + class_name, content)
            if class_comment_match:
                class_doc = self._clean_comment(class_comment_match.group(1))
            
            # Extraire les méthodes
            class_content = self._extract_class_content(content, class_name)
            methods = self._extract_methods(class_content)
            
            # Extraire les propriétés
            properties = self._extract_properties(class_content)
            
            classes[class_name] = {
                'doc': class_doc,
                'methods': methods,
                'properties': properties
            }
        
        # Stocker les informations du module
        module_name = file_path.stem
        self.modules[module_name] = {
            'path': str(file_path.relative_to(self.js_dir.parent)),
            'doc': module_doc,
            'classes': classes
        }
    
    def _extract_class_content(self, content, class_name):
        """Extrait le contenu d'une classe"""
        class_start = content.find(f"class {class_name}")
        if class_start == -1:
            return ""
        
        # Trouver la fin de la classe en comptant les accolades
        open_braces = 0
        class_end = class_start
        in_class = False
        
        for i in range(class_start, len(content)):
            if content[i] == '{' and not in_class:
                in_class = True
                open_braces = 1
            elif content[i] == '{' and in_class:
                open_braces += 1
            elif content[i] == '}' and in_class:
                open_braces -= 1
                if open_braces == 0:
                    class_end = i + 1
                    break
        
        return content[class_start:class_end]
    
    def _extract_methods(self, class_content):
        """Extrait les méthodes d'une classe"""
        methods = {}
        method_matches = self.method_pattern.findall(class_content)
        
        for method_name in method_matches:
            # Ignorer le constructeur
            if method_name == 'constructor':
                continue
            
            # Chercher le commentaire de méthode précédent
            method_doc = ""
            method_pattern = re.compile(r'/\*\*([\s\S]*?)\*/\s*' + method_name + '\s*\(')
            method_comment_match = method_pattern.search(class_content)
            if method_comment_match:
                method_doc = self._clean_comment(method_comment_match.group(1))
            
            methods[method_name] = {
                'doc': method_doc
            }
        
        return methods
    
    def _extract_properties(self, class_content):
        """Extrait les propriétés d'une classe"""
        properties = {}
        property_matches = self.property_pattern.findall(class_content)
        
        for prop_name in property_matches:
            # Chercher la valeur de la propriété
            prop_value = ""
            prop_pattern = re.compile(r'this\.' + prop_name + '\s*=\s*([^;]+);')
            prop_value_match = prop_pattern.search(class_content)
            if prop_value_match:
                prop_value = prop_value_match.group(1).strip()
            
            properties[prop_name] = {
                'value': prop_value
            }
        
        return properties
    
    def _clean_comment(self, comment):
        """Nettoie un commentaire JSDoc"""
        lines = comment.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Supprimer les astérisques et les espaces en début de ligne
            cleaned_line = re.sub(r'^\s*\*\s?', '', line)
            if cleaned_line.strip():
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def generate_markdown(self):
        """Génère la documentation au format Markdown"""
        for module_name, module_info in self.modules.items():
            self._generate_module_doc(module_name, module_info)
        
        # Générer un index des modules
        self._generate_index()
    
    def _generate_module_doc(self, module_name, module_info):
        """Génère la documentation d'un module"""
        output_file = self.output_dir / f"{module_name}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # En-tête du module
            f.write(f"# Module {module_name}\n\n")
            
            # Chemin du fichier
            f.write(f"**Fichier:** `{module_info['path']}`\n\n")
            
            # Description du module
            if module_info['doc']:
                f.write(f"{module_info['doc']}\n\n")
            
            # Table des matières
            f.write("## Table des matières\n\n")
            for class_name in module_info['classes']:
                f.write(f"- [{class_name}](#{class_name.lower()})\n")
            f.write("\n")
            
            # Documentation des classes
            for class_name, class_info in module_info['classes'].items():
                f.write(f"## {class_name}\n\n")
                
                # Description de la classe
                if class_info['doc']:
                    f.write(f"{class_info['doc']}\n\n")
                
                # Propriétés
                if class_info['properties']:
                    f.write("### Propriétés\n\n")
                    f.write("| Nom | Valeur | Description |\n")
                    f.write("|-----|--------|-------------|\n")
                    
                    for prop_name, prop_info in class_info['properties'].items():
                        f.write(f"| `{prop_name}` | `{prop_info['value']}` | |\n")
                    
                    f.write("\n")
                
                # Méthodes
                if class_info['methods']:
                    f.write("### Méthodes\n\n")
                    
                    for method_name, method_info in class_info['methods'].items():
                        f.write(f"#### `{method_name}()`\n\n")
                        
                        if method_info['doc']:
                            f.write(f"{method_info['doc']}\n\n")
        
        logger.info(f"Documentation générée pour le module {module_name}: {output_file}")
    
    def _generate_index(self):
        """Génère un index des modules"""
        output_file = self.output_dir / "index.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Documentation JavaScript du Projet Madsea\n\n")
            f.write("## Modules\n\n")
            
            for module_name, module_info in self.modules.items():
                # Extraire une courte description du module
                description = ""
                if module_info['doc']:
                    description = module_info['doc'].split('\n')[0]
                
                f.write(f"- [{module_name}]({module_name}.md): {description}\n")
        
        logger.info(f"Index de documentation généré: {output_file}")
    
    def generate_json(self):
        """Génère la documentation au format JSON"""
        output_file = self.output_dir / "js_documentation.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.modules, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Documentation JSON générée: {output_file}")


def main():
    """Point d'entrée principal du script"""
    parser = argparse.ArgumentParser(description="Générateur de documentation JavaScript")
    parser.add_argument(
        "--js-dir", "-j", type=str, default="ui/static/js",
        help="Répertoire contenant les fichiers JavaScript"
    )
    parser.add_argument(
        "--output-dir", "-o", type=str, default="docs/js",
        help="Répertoire de sortie pour la documentation"
    )
    parser.add_argument(
        "--format", "-f", type=str, choices=["markdown", "json", "both"], default="both",
        help="Format de sortie de la documentation"
    )
    args = parser.parse_args()
    
    # Créer le générateur de documentation
    doc_generator = JSDocGenerator(args.js_dir, args.output_dir)
    
    # Analyser les fichiers JavaScript
    doc_generator.parse_js_files()
    
    # Générer la documentation
    if args.format in ["markdown", "both"]:
        doc_generator.generate_markdown()
    
    if args.format in ["json", "both"]:
        doc_generator.generate_json()
    
    logger.info(f"Documentation générée avec succès dans {args.output_dir}")


if __name__ == "__main__":
    main()