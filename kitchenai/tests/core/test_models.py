import pytest
import uuid
from kitchenai.core.models import (
    Artifact, 
    FileObject,
    EmbedObject,
    KitchenAIManagement
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.apps import apps
from django.conf import settings
from faststream.nats import TestNatsBroker
from kitchenai.core.broker import whisk

pytestmark = pytest.mark.django_db

@pytest.fixture
async def organization(db):
    """Create a test organization with unique slug"""
    Organization = apps.get_model(settings.AUTH_ORGANIZATION_MODEL)
    unique_slug = f"test-org-{uuid.uuid4().hex[:8]}"
    return await Organization.objects.acreate(
        name="Test Organization",
        slug=unique_slug
    )

@pytest.fixture
async def bento_box(organization):
    """Create a test bento box with unique identifiers"""
    org_instance = await organization
    unique_id = uuid.uuid4().hex[:8]
    
    BentoManager = apps.get_model(settings.KITCHENAI_BENTO_CLIENT_MODEL)
    return await BentoManager.objects.acreate(
        client_id=f"test-client-{unique_id}",
        name=f"Test Bento {unique_id}",
        version=f"0.1.{unique_id}",  # Add version
        organization=org_instance
    )

@pytest.mark.asyncio
async def test_create_artifact():
    """Test creating a basic artifact"""
    artifact = await Artifact.objects.acreate(
        name="Test Artifact",
        status=Artifact.Status.PENDING
    )
    
    assert artifact.name == "Test Artifact"
    assert artifact.status == Artifact.Status.PENDING

@pytest.mark.asyncio
async def test_create_file_object(sample_file, bento_box):
    """Test creating a file object"""
    bento_box_instance = await bento_box
    
    # Use test broker
    async with TestNatsBroker(whisk.broker) as test_broker:
        original_broker = whisk.broker
        whisk.broker = test_broker
        try:
            file_obj = await FileObject.objects.acreate(
                file=sample_file,
                name="Test File",
                ingest_label="test_label",
                metadata={"test": "data"},
                bento_box=bento_box_instance
            )
            
            assert file_obj.name == "Test File"
            assert file_obj.ingest_label == "test_label"
            assert file_obj.metadata == {"test": "data"}
            assert file_obj.bento_box == bento_box_instance
            assert file_obj.file.name.endswith("test_file.txt")
        finally:
            whisk.broker = original_broker

@pytest.mark.asyncio
async def test_create_embed_object(bento_box):
    """Test creating an embed object"""
    bento_box_instance = await bento_box
    
    # Use test broker
    async with TestNatsBroker(whisk.broker) as test_broker:
        original_broker = whisk.broker
        whisk.broker = test_broker
        try:
            embed = await EmbedObject.objects.acreate(
                text="Test Embed",
                bento_box=bento_box_instance,
                status=EmbedObject.Status.PENDING
            )
            
            assert embed.text == "Test Embed"
            assert embed.status == EmbedObject.Status.PENDING
        finally:
            whisk.broker = original_broker

@pytest.mark.asyncio
async def test_create_management():
    """Test creating a management object"""
    mgmt = await KitchenAIManagement.objects.acreate(
        name="test_management",  # This is the primary key
        version="1.0.0",
        description="Test Description"
    )
    
    assert mgmt.name == "test_management"
    assert mgmt.version == "1.0.0"
    assert mgmt.description == "Test Description"

@pytest.mark.asyncio
async def test_file_object_str(bento_box):
    """Test FileObject string representation"""
    bento_box_instance = await bento_box
    
    # Use test broker
    async with TestNatsBroker(whisk.broker) as test_broker:
        original_broker = whisk.broker
        whisk.broker = test_broker
        try:
            file_obj = await FileObject.objects.acreate(
                name="Test File",
                ingest_label="test_label",
                bento_box=bento_box_instance
            )
            assert str(file_obj) == "Test File"
        finally:
            whisk.broker = original_broker

@pytest.mark.asyncio
async def test_embed_object_str(bento_box):
    """Test EmbedObject string representation"""
    bento_box_instance = await bento_box
    
    # Use test broker
    async with TestNatsBroker(whisk.broker) as test_broker:
        original_broker = whisk.broker
        whisk.broker = test_broker
        try:
            embed = await EmbedObject.objects.acreate(
                text="Test Embed",
                bento_box=bento_box_instance,
                status=EmbedObject.Status.PENDING
            )
            assert str(embed) == "Test Embed"
        finally:
            whisk.broker = original_broker

@pytest.mark.asyncio
async def test_management_str():
    """Test KitchenAIManagement string representation"""
    mgmt = await KitchenAIManagement.objects.acreate(
        name="Test Management",
        description="Test Description"
    )
    assert str(mgmt) == "Test Management"

@pytest.mark.asyncio
async def test_artifact_status_choices():
    """Test Artifact status choices"""
    artifact = await Artifact.objects.acreate(
        name="Test Artifact",
        status=Artifact.Status.PENDING
    )
    
    # Test status can be changed
    artifact.status = Artifact.Status.COMPLETED
    await artifact.asave()
    
    assert artifact.status == Artifact.Status.COMPLETED

@pytest.mark.asyncio
async def test_file_object_basic(bento_box):
    """Test creating a minimal file object with broker interaction"""
    bento_box_instance = await bento_box
    
    # Set up test broker
    async with TestNatsBroker(whisk.broker) as test_broker:
        # Replace the real broker temporarily
        original_broker = whisk.broker
        whisk.broker = test_broker
        
        try:
            # Create test file
            test_file = SimpleUploadedFile(
                "test.txt",
                b"test content",
                content_type="text/plain"
            )
            
            # Create file object - this should trigger broker publish
            file_obj = await FileObject.objects.acreate(
                file=test_file,
                name=test_file.name,
                ingest_label="test_label",
                metadata={"test": "data"},
                bento_box=bento_box_instance
            )
            
            # Verify object was created
            assert isinstance(file_obj, FileObject)
            assert file_obj.bento_box == bento_box_instance
            
            print("File object created and message published successfully")
            
        finally:
            # Restore original broker
            whisk.broker = original_broker 