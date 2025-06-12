"""
Main analyzer for CLAMBA - Smart Legal Contract Automaton Generator
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..ai.factory import AIProviderFactory
from ..config.settings import CLAMBAConfig
from ..models.contract import Contract, ContractResult, ContractType
from ..models.process import ProcessAnalysisResult
from ..utils.logger import get_logger
from ..utils.validator import ResultValidator
from .pdf_extractor import PDFExtractor
from .process_detector import ProcessDetector


class CLAMBAAnalyzer:
    """
    Main analyzer for generating Smart Legal Contract Automatons
    
    This class orchestrates the entire analysis process:
    1. PDF text extraction
    2. Business process detection
    3. Dependency analysis
    4. Automaton generation
    """
    
    def __init__(self, config: CLAMBAConfig):
        """
        Initialize the analyzer
        
        Args:
            config: CLAMBA configuration
        """
        self.config = config
        self.logger = get_logger(__name__, debug=config.debug)
        
        # Initialize components
        self.pdf_extractor = PDFExtractor()
        self.ai_provider = AIProviderFactory.create_provider(config)
        self.process_detector = ProcessDetector(self.ai_provider, config)
        self.validator = ResultValidator()
        
        self.logger.info("CLAMBA Analyzer initialized")
        self.logger.info(f"AI Provider: {config.ai.provider}")
        self.logger.info(f"Debug mode: {config.debug}")

    def analyze_contract(
        self,
        pdf_path: Union[str, Path],
        contract_type: Optional[ContractType] = None,
        custom_instructions: Optional[str] = None,
    ) -> ContractResult:
        """
        Analyze a contract PDF and generate automatons
        
        Args:
            pdf_path: Path to the PDF contract
            contract_type: Optional contract type hint
            custom_instructions: Optional custom analysis instructions
            
        Returns:
            ContractResult with generated automatons
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If analysis fails
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.logger.info(f"🔍 Starting contract analysis: {pdf_path.name}")
        
        try:
            # Step 1: Extract text from PDF
            contract_text = self._extract_pdf_text(pdf_path)
            
            # Step 2: Detect business processes
            process_result = self._detect_processes(
                contract_text, contract_type, custom_instructions
            )
            
            # Step 3: Analyze dependencies
            dependencies = self._analyze_dependencies(process_result.processes)
            
            # Step 4: Generate automatons
            contract = self._generate_automatons(
                process_result.processes, dependencies, pdf_path.stem
            )
            
            # Step 5: Validate result
            self._validate_result(contract)
            
            result = ContractResult(
                contract=contract,
                process_analysis=process_result,
                dependencies=dependencies,
                metadata={
                    "source_file": str(pdf_path),
                    "contract_type": contract_type.value if contract_type else "auto",
                    "analysis_date": datetime.now().isoformat(),
                    "ai_provider": self.config.ai.provider,
                    "ai_model": self._get_ai_model_name(),
                    "custom_instructions": custom_instructions,
                }
            )
            
            self.logger.info("✅ Contract analysis completed successfully")
            self.logger.info(f"Generated {len(contract.automates)} automatons")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analysis failed: {str(e)}")
            raise ValueError(f"Contract analysis failed: {str(e)}") from e

    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF"""
        self.logger.info("📄 Extracting PDF text...")
        
        text = self.pdf_extractor.extract_text(pdf_path)
        
        if not text.strip():
            raise ValueError("No text extracted from PDF")
        
        self.logger.info(f"✅ PDF text extracted: {len(text)} characters")
        return text

    def _detect_processes(
        self,
        contract_text: str,
        contract_type: Optional[ContractType],
        custom_instructions: Optional[str],
    ) -> ProcessAnalysisResult:
        """Detect business processes in the contract"""
        self.logger.info("🔍 Detecting business processes...")
        
        result = self.process_detector.detect_processes(
            contract_text, contract_type, custom_instructions
        )
        
        self.logger.info(f"✅ Detected {len(result.processes)} processes")
        for i, process in enumerate(result.processes, 1):
            self.logger.debug(f"   {i}. {process.name} ({len(process.steps)} steps)")
        
        return result

    def _analyze_dependencies(self, processes: List) -> Dict[str, List[str]]:
        """Analyze dependencies between processes"""
        self.logger.info("🔗 Analyzing process dependencies...")
        
        dependencies = self.process_detector.analyze_dependencies(processes)
        
        # Log dependencies
        for process_id, deps in dependencies.items():
            if deps:
                process_name = next(
                    (p.name for p in processes if p.id == process_id), "Unknown"
                )
                dep_names = [
                    next((p.name for p in processes if p.id == dep_id), dep_id)
                    for dep_id in deps
                ]
                self.logger.debug(f"   🔗 {process_name} depends on: {', '.join(dep_names)}")
            else:
                process_name = next(
                    (p.name for p in processes if p.id == process_id), "Unknown"
                )
                self.logger.debug(f"   🆓 {process_name} is independent")
        
        self.logger.info("✅ Dependencies analyzed")
        return dependencies

    def _generate_automatons(
        self, processes: List, dependencies: Dict[str, List[str]], contract_name: str
    ) -> Contract:
        """Generate automatons from processes"""
        self.logger.info("⚙️ Generating automatons...")
        
        from ..models.automate import Automate
        from ..utils.sanitizer import IDSanitizer
        
        sanitizer = IDSanitizer()
        automates = []
        
        for process in processes:
            # Create automaton
            automate = Automate.from_process(
                process, dependencies.get(process.id, []), sanitizer
            )
            automates.append(automate)
            
            self.logger.debug(f"   ✅ Automate {automate.id}: {automate.name}")
        
        # Create contract
        contract = Contract(
            id=sanitizer.sanitize(f"contract-{contract_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            name=contract_name.replace("_", " ").title(),
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="clamba-ai",
            description=f"Contract generated by CLAMBA - {len(automates)} automatons detected",
            automates=automates,
        )
        
        self.logger.info(f"✅ Generated {len(automates)} automatons")
        return contract

    def _validate_result(self, contract: Contract) -> None:
        """Validate the generated contract"""
        self.logger.info("🔍 Validating result...")
        
        validation_errors = self.validator.validate_contract(contract)
        
        if validation_errors:
            error_msg = "Validation failed:\n" + "\n".join(validation_errors)
            raise ValueError(error_msg)
        
        self.logger.info("✅ Result validation passed")

    def _get_ai_model_name(self) -> str:
        """Get the AI model name"""
        ai_config = self.config.get_ai_config()
        return ai_config.model

    def save_result(
        self,
        result: ContractResult,
        output_path: Union[str, Path],
        include_metadata: Optional[bool] = None,
    ) -> None:
        """
        Save analysis result to file
        
        Args:
            result: Contract analysis result
            output_path: Output file path
            include_metadata: Whether to include metadata (default from config)
        """
        output_path = Path(output_path)
        
        if include_metadata is None:
            include_metadata = self.config.output.include_metadata
        
        # Prepare data for export
        export_data = result.contract.dict()
        
        if include_metadata:
            export_data["metadata"] = result.metadata
            export_data["process_analysis"] = {
                "detection_method": result.process_analysis.detection_method,
                "confidence_score": result.process_analysis.confidence_score,
                "analysis_time_seconds": result.process_analysis.analysis_time_seconds,
            }
            export_data["dependencies"] = result.dependencies
        
        # Save based on format
        if self.config.output.output_format == "yaml":
            import yaml
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(export_data, f, default_flow_style=False, indent=2)
        else:  # JSON
            with open(output_path, "w", encoding="utf-8") as f:
                if self.config.output.pretty_print:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(export_data, f, ensure_ascii=False)
        
        self.logger.info(f"💾 Result saved to: {output_path}")

    def analyze_multiple_contracts(
        self,
        pdf_paths: List[Union[str, Path]],
        output_dir: Union[str, Path],
        contract_types: Optional[Dict[str, ContractType]] = None,
    ) -> List[ContractResult]:
        """
        Analyze multiple contracts in batch
        
        Args:
            pdf_paths: List of PDF file paths
            output_dir: Output directory for results
            contract_types: Optional mapping of file names to contract types
            
        Returns:
            List of contract analysis results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        contract_types = contract_types or {}
        
        self.logger.info(f"🔄 Starting batch analysis of {len(pdf_paths)} contracts")
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            pdf_path = Path(pdf_path)
            
            self.logger.info(f"📄 Processing {i}/{len(pdf_paths)}: {pdf_path.name}")
            
            try:
                # Get contract type for this file
                contract_type = contract_types.get(pdf_path.name)
                
                # Analyze contract
                result = self.analyze_contract(pdf_path, contract_type)
                results.append(result)
                
                # Save individual result
                output_file = output_dir / f"{pdf_path.stem}_automates.json"
                self.save_result(result, output_file)
                
                self.logger.info(f"✅ Completed {pdf_path.name}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to process {pdf_path.name}: {str(e)}")
                continue
        
        # Save batch summary
        summary = {
            "batch_analysis": {
                "total_contracts": len(pdf_paths),
                "successful_analyses": len(results),
                "failed_analyses": len(pdf_paths) - len(results),
                "analysis_date": datetime.now().isoformat(),
                "ai_provider": self.config.ai.provider,
            },
            "results": [
                {
                    "contract_id": result.contract.id,
                    "contract_name": result.contract.name,
                    "automates_count": len(result.contract.automates),
                    "source_file": result.metadata.get("source_file"),
                }
                for result in results
            ],
        }
        
        summary_file = output_dir / "batch_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"🎊 Batch analysis completed: {len(results)}/{len(pdf_paths)} successful")
        self.logger.info(f"📊 Summary saved to: {summary_file}")
        
        return results

    def get_supported_contract_types(self) -> List[ContractType]:
        """Get list of supported contract types"""
        return list(ContractType)

    def validate_configuration(self) -> Dict[str, bool]:
        """
        Validate the current configuration
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            "ai_provider_available": False,
            "ai_config_valid": False,
            "pdf_extractor_available": True,  # Always available
        }
        
        try:
            # Test AI provider connection
            validation["ai_provider_available"] = self.ai_provider.test_connection()
            validation["ai_config_valid"] = self.config.validate_ai_config()
        except Exception as e:
            self.logger.error(f"Configuration validation error: {str(e)}")
        
        return validation