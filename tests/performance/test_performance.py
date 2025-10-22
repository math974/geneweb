"""
Tests de performance pour le système GWU.
"""

import pytest
import time
import tempfile
import os
from pathlib import Path
from geneweb.gwu.adapters.input.gw_file_repository import GwFilePersonRepository, GwFileFamilyRepository
from geneweb.gwu.adapters.output.gw_writer_clean import GwWriterClean
from geneweb.gwu.adapters.output.gw_writer import GwWriterOptions


class TestPerformance:
    """Tests de performance pour le système GWU."""
    
    def test_export_performance_small_dataset(self, sample_persons, sample_families, gw_writer_options):
        """Test de performance avec un petit jeu de données."""
        writer = GwWriterClean(gw_writer_options)
        
        start_time = time.time()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, sample_families, sample_persons)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Vérifier que l'export s'est terminé rapidement (moins de 1 seconde)
            assert execution_time < 1.0, f"Export trop lent: {execution_time:.2f}s"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_export_performance_medium_dataset(self, galichet_gw_file, gw_writer_options):
        """Test de performance avec un jeu de données moyen."""
        # Charger les données
        person_repo = GwFilePersonRepository(galichet_gw_file)
        family_repo = GwFileFamilyRepository(galichet_gw_file)
        
        persons = list(person_repo.get_all())
        families = list(family_repo.get_all())
        
        writer = GwWriterClean(gw_writer_options)
        
        start_time = time.time()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, families, persons)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Vérifier que l'export s'est terminé rapidement (moins de 5 secondes)
            assert execution_time < 5.0, f"Export trop lent: {execution_time:.2f}s"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_memory_usage_small_dataset(self, sample_persons, sample_families, gw_writer_options):
        """Test d'utilisation mémoire avec un petit jeu de données."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        writer = GwWriterClean(gw_writer_options)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, sample_families, sample_persons)
            
            final_memory = process.memory_info().rss
            memory_usage = final_memory - initial_memory
            
            # Vérifier que l'utilisation mémoire est raisonnable (moins de 50MB)
            assert memory_usage < 50 * 1024 * 1024, f"Utilisation mémoire excessive: {memory_usage / 1024 / 1024:.2f}MB"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_memory_usage_medium_dataset(self, galichet_gw_file, gw_writer_options):
        """Test d'utilisation mémoire avec un jeu de données moyen."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Charger les données
        person_repo = GwFilePersonRepository(galichet_gw_file)
        family_repo = GwFileFamilyRepository(galichet_gw_file)
        
        persons = list(person_repo.get_all())
        families = list(family_repo.get_all())
        
        writer = GwWriterClean(gw_writer_options)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, families, persons)
            
            final_memory = process.memory_info().rss
            memory_usage = final_memory - initial_memory
            
            # Vérifier que l'utilisation mémoire est raisonnable (moins de 100MB)
            assert memory_usage < 100 * 1024 * 1024, f"Utilisation mémoire excessive: {memory_usage / 1024 / 1024:.2f}MB"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_concurrent_exports(self, sample_persons, sample_families, gw_writer_options):
        """Test d'exports concurrents."""
        import threading
        import queue
        
        def export_worker(result_queue):
            """Worker pour l'export."""
            try:
                writer = GwWriterClean(gw_writer_options)
                
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                    temp_file = f.name
                
                with open(temp_file, 'w') as f:
                    writer.write_database(f, sample_families, sample_persons)
                
                result_queue.put(("success", temp_file))
                
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        # Lancer plusieurs exports en parallèle
        num_threads = 3
        result_queue = queue.Queue()
        threads = []
        
        for _ in range(num_threads):
            thread = threading.Thread(target=export_worker, args=(result_queue,))
            thread.start()
            threads.append(thread)
        
        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()
        
        # Vérifier les résultats
        success_count = 0
        temp_files = []
        
        while not result_queue.empty():
            result_type, result_data = result_queue.get()
            
            if result_type == "success":
                success_count += 1
                temp_files.append(result_data)
            else:
                pytest.fail(f"Erreur dans l'export concurrent: {result_data}")
        
        # Vérifier que tous les exports ont réussi
        assert success_count == num_threads, f"Seulement {success_count}/{num_threads} exports ont réussi"
        
        # Nettoyer les fichiers temporaires
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_large_dataset_handling(self, gw_writer_options):
        """Test de gestion d'un grand jeu de données."""
        # Créer un grand jeu de données
        large_persons = []
        large_families = []
        
        for i in range(1000):  # 1000 personnes
            person = Person(
                id=f"P{i}",
                surname=f"Surname{i}",
                first_name=f"FirstName{i}",
                occ=0,
                birth=Date(1900 + (i % 100), 1, 1),
                death=None,
                notes=f"Notes for person {i}",
                events=[]
            )
            large_persons.append(person)
        
        for i in range(500):  # 500 familles
            family = Family(
                id=f"F{i}",
                father_id=f"P{i*2}",
                mother_id=f"P{i*2+1}",
                children_ids=[f"P{i*2+2}"] if i*2+2 < 1000 else [],
                marriage=Event("marr", Date(1920 + (i % 80), 1, 1)),
                notes=f"Family notes {i}"
            )
            large_families.append(family)
        
        writer = GwWriterClean(gw_writer_options)
        
        start_time = time.time()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with open(temp_file, 'w') as f:
                writer.write_database(f, large_families, large_persons)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Vérifier que l'export s'est terminé en temps raisonnable (moins de 30 secondes)
            assert execution_time < 30.0, f"Export trop lent: {execution_time:.2f}s"
            
            # Vérifier que le fichier a été créé
            assert os.path.exists(temp_file)
            
            # Vérifier la taille du fichier
            file_size = os.path.getsize(temp_file)
            assert file_size > 0, "Le fichier de sortie est vide"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
